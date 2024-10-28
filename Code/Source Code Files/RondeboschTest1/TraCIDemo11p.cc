//
// Copyright (C) 2006-2011 Christoph Sommer <christoph.sommer@uibk.ac.at>
//
// Documentation for these modules is at http://veins.car2x.org/
//
// SPDX-License-Identifier: GPL-2.0-or-later
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//

#include "veins/modules/application/traci/TraCIDemo11p.h"

#include "veins/modules/application/traci/TraCIDemo11pMessage_m.h"

using namespace omnetpp;

using namespace veins;

Define_Module(veins::TraCIDemo11p);

void TraCIDemo11p::initialize(int stage) {
    DemoBaseApplLayer::initialize(stage);
    if (stage == 0) {
        sentMessage = false;
        lastDroveAt = simTime();
        currentSubscribedServiceId = -1;
    }
}

void TraCIDemo11p::onWSA(DemoServiceAdvertisment *wsa) {
    if (currentSubscribedServiceId == -1) {
        mac->changeServiceChannel(
                static_cast<Channel>(wsa->getTargetChannel()));
        currentSubscribedServiceId = wsa->getPsid();
        if (currentOfferedServiceId != wsa->getPsid()) {
            stopService();
            startService(static_cast<Channel>(wsa->getTargetChannel()),
                    wsa->getPsid(), "Mirrored Traffic Service");
        }
    }
}

void TraCIDemo11p::onWSM(BaseFrame1609_4 *frame) {
    TraCIDemo11pMessage *wsm = check_and_cast<TraCIDemo11pMessage*>(frame);

    simtime_t time;
    double distance;
    if (wsm->getSenderID() == 2 && getParentModule()->getIndex()!=2) {
        distance = wsm->getSenderPos().distance(
                mobility->getPositionAt(simTime()));
        findHost()->getDisplayString().setTagArg("i", 1, "blue");
        if (distance <= 500 && traciVehicle->getSpeed() != 0) {
            getParentModule()->bubble("Slowing Down!");
            double vehicle_distance = traci->getDistance(
                    mobility->getPositionAt(simTime()), wsm->getSenderPos(),
                    true);
            //Calculate time needed by ambulance to reach the distance to the vehicle
            double v0 = wsm->getSenderSpeed();
            double a = wsm->getSenderAcceleration() / 2;
            double sol1 = ((-1.0 * v0)
                    + sqrt(pow(v0, 2) - 4 * a * (-1.0 * vehicle_distance))) / 2;
            double sol2 = ((1.0 * v0)
                    + sqrt(pow(v0, 2) - 4 * a * (-1.0 * vehicle_distance))) / 2;
            if (sol1 > sol2) {
                time = int(sol1);
            } else {
                time = int(sol2);
            }
            if (time <= 0)
                traciVehicle->setSpeed(0);
            else
                traciVehicle->slowDown(5, time);
            getParentModule()->bubble("Slowing down!");
        } else {
            traciVehicle->setSpeedMode(0x1f);
            traciVehicle->setSpeed(16);
        }
    }
    if (wsm->getSenderID() == 0 && getParentModule()->getIndex()!=0) {
        findHost()->getDisplayString().setTagArg("i", 1, "green");
        getParentModule()->bubble("Recalculating route...");
        traci->lane("main22a_0").setDisallowed(setDisallowedVehicles);
        traci->lane("main22b_0").setDisallowed(setDisallowedVehicles);
        traci->lane("main22b_1").setDisallowed(setDisallowedVehicles);
        traciVehicle->changeTarget(traciVehicle->getPlannedRoadIds().back());
    }
    if (!sentMessage){
        sentMessage = true;
        wsm->setSenderAddress(myId);
        wsm->setSerial(3);
        scheduleAt(simTime()+2+uniform(0.01, 0.2), wsm->dup());
    }
}

void TraCIDemo11p::handleSelfMsg(cMessage *msg) {
    if (TraCIDemo11pMessage *wsm = dynamic_cast<TraCIDemo11pMessage*>(msg)) {
        // send this message on the service channel until the counter is 3 or higher.
        // this code only runs when channel switching is enabled
        sendDown(wsm->dup());
        wsm->setSerial(wsm->getSerial() + 1);
        if (wsm->getSerial() >= 3) {
            // stop service advertisements
            stopService();
            delete (wsm);
        } else {
            scheduleAt(simTime() + 1, wsm);
        }
    } else {
        DemoBaseApplLayer::handleSelfMsg(msg);
    }
}

void TraCIDemo11p::handlePositionUpdate(cObject *obj) {
    DemoBaseApplLayer::handlePositionUpdate(obj);
    nodeID = getParentModule()->getIndex();

    if (nodeID == 2) {
        traciVehicle->setSpeedMode(0b100111);
        traciVehicle->setSpeed(25);
        if (int(simTime().dbl()) % 6 == 0 && (int(simTime().dbl()) % 5 != 0)) {
            findHost()->getDisplayString().setTagArg("i", 1, "red");
            TraCIDemo11pMessage *wsm = new TraCIDemo11pMessage();
            populateWSM(wsm);
            wsm->setSenderRoadID(traciVehicle->getRoadId().c_str());
            wsm->setSenderSpeed(traciVehicle->getSpeed());
            wsm->setSenderAcceleration(traciVehicle->getAcceleration());
            wsm->setSenderPos(mobility->getPositionAt(simTime()));
            wsm->setSenderID(nodeID);
            sendDown(wsm);
            getParentModule()->bubble("Sending Safety Message!");
            sentMessage = true;
        }
    }
    if (nodeID == 0) {
        if (traciVehicle->getLaneId() == "main22b_0") {
            if (traciVehicle->getSpeed() == 0)
                getParentModule()->bubble(
                        "Sending crash location for rerouting...");
            else
                getParentModule()->bubble(
                        "Crashed! Sending crash location for rerouting...");
            traciVehicle->setSpeedMode(0x1f);
            traciVehicle->setSpeed(0);
            findHost()->getDisplayString().setTagArg("i", 1, "orange");
            if (int(simTime().dbl()) % 5 == 0
                    && (int(simTime().dbl()) % 6 != 0)) {
                TraCIDemo11pMessage *crash = new TraCIDemo11pMessage();
                populateWSM(crash);
                crash->setSenderID(nodeID);
                sendDown(crash);
                sentMessage=true;
            }
        }
    }
}
