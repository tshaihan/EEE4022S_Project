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

    findHost()->getDisplayString().setTagArg("i", 1, "green");

    /*if (mobility->getRoadId()[0] != ':') traciVehicle->changeRoute(wsm->getDemoData(), 9999);
     if (!sentMessage) {
     sentMessage = true;
     // repeat the received traffic update once in 2 seconds plus some random delay
     wsm->setSenderAddress(myId);
     wsm->setSerial(3);
     scheduleAt(simTime() + 2 + uniform(0.01, 0.2), wsm->dup());
     }*/

    int senderID = wsm->getSenderID();
    disallowedClasses.push_back(dc);

    if (getParentModule()->getIndex() != 0) {
        findHost()->getDisplayString().setTagArg("i", 1, "red");
        traciVehicle->setSpeedMode(0x1f);
        traciVehicle->setMaxSpeed(16);
        traciVehicle->setColor(TraCIColor::fromTkColor("red"));
        traci->lane("main23a_0").setDisallowed(disallowedClasses);
        traci->lane("main23b_0").setDisallowed(disallowedClasses);
        traci->lane("main23b_1").setDisallowed(disallowedClasses);
        traciVehicle->changeTarget("4765012#1");
        /*if (senderID == 2)
        {
            findHost()->getDisplayString().setTagArg("t", 1, "Received emergency message!");
            traciVehicle->setSpeedMode(0x1f);
            traciVehicle->setSpeed(10);
        }*/
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

    int nodeID = getParentModule()->getIndex();

    if (nodeID == 2)
    {
        if (simTime() == 10 || simTime() == 20 || simTime() == 30 || simTime() == 40 || simTime() == 50 || simTime() == 60 || simTime() == 70 || simTime() == 80)
        {
            TraCIDemo11pMessage *emergency = new TraCIDemo11pMessage();
            populateWSM(emergency);
            emergency->setSenderID(nodeID);
            sendDown(emergency);
        }
    }
    if (nodeID == 0) {
        if (simTime() == 20) {
            EV_INFO << traciVehicle->getRouteId();
            TraCIDemo11pMessage *wsm = new TraCIDemo11pMessage();
            populateWSM(wsm);
            wsm->setSenderID(nodeID);
            sendDown(wsm);
            traciVehicle->setSpeedMode(0x1f);
            traciVehicle->setSpeed(0);
        }
        if (simTime() == 175) {
            traci->lane("main23b_0").setDisallowed(allowedClasses);
            traci->lane("main23b_1").setDisallowed(allowedClasses);
            traci->lane("main23a_0").setDisallowed(allowedClasses);
            traciVehicle->changeTarget("rosendale2a");
            traciVehicle->setSpeedMode(0x1f);
            traciVehicle->setSpeed(16);
        }
    } else if (simTime() == 175 && nodeID == 1) {
        traci->lane("main23b_0").setDisallowed(allowedClasses);
        traci->lane("main23b_1").setDisallowed(allowedClasses);
        traci->lane("main23a_0").setDisallowed(allowedClasses);
        traciVehicle->changeTarget("4765012#1");
    }
        else{
        lastDroveAt = simTime();
    }
}
