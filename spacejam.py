from direct.showbase.ShowBase import ShowBase
import math, sys, random
import DefensePaths as defensePaths
import SpaceJamClasses as spaceJamClasses
import Player as myPlayer
from panda3d.core import CollisionTraverser, CollisionHandlerPusher
from CollideObjectBase import PlacedObject

class SpaceJam(ShowBase): #Constructor
    def __init__(self):
        ShowBase.__init__(self)

        self.traverser = CollisionTraverser()
        self.cTrav = self.traverser
        self.traverser.traverse(self.render)
        self.pusher = CollisionHandlerPusher()
        
        self.SetupScene()
        
        self.SetCamera()

        fullCycle = 60

        x = 0
        for j in range(fullCycle):
            spaceJamClasses.Drone.droneCount += 1
            nickName = "Drone" + str(spaceJamClasses.Drone.droneCount)
            #self.DrawCloudDefense(self.Planet1, nickName)
            self.DrawBaseballSeams(self.Station, nickName, j, fullCycle, 1)
        self.DrawCircleXY()
        self.DrawCircleXZ()
        self.DrawCircleYZ()
        # Colliders.

        self.pusher.addCollider(self.Player.collisionNode, self.Player.modelNode)
        self.traverser.addCollider(self.Player.collisionNode, self.pusher)

        #self.traverser.showCollisions(self.render)

    def SetCamera(self):
        #self.disableMouse()
        self.camera.reparentTo(self.Player.modelNode)
        self.camera.setFluidPos(0, 1, 0)

    def DrawCloudDefense(self, centralObject, droneName):
        unitVec = defensePaths.Cloud()
        unitVec.normalize()
        position = unitVec * 500 + centralObject.modelNode.getPos()
        spaceJamClasses.Drone(self.loader, "./Assets/Drones/JulesVerne.obj", self.render, droneName, "./Assets/Drones/Textures/sh3.jpg", position, 100)
    def DrawBaseballSeams(self, centralObject, droneName, step, numSeams, radius = 1):
        unitVec = defensePaths.BaseballSeams(step, numSeams, B = 0.4)
        unitVec.normalize()
        position = unitVec * radius * 1000 + centralObject.modelNode.getPos()
        spaceJamClasses.Drone(self.loader, "./Assets/Drones/JulesVerne.obj", self.render, droneName, "./Assets/Drones/Textures/sh3.jpg", position, 200)

    def DrawCircleXY(self):
        self.parent = self.loader.loadModel("./Assets/Drones/JulesVerne.obj")
        self.parent.setScale(5)
        a = 0.0
        aInc = 0.2
        R = 50.0

        for i in range(33):
            posVec = (R * math.cos(a), R * math.sin(a), 0)
            self.placeholder = self.render.attachNewNode("Placeholder")
            self.placeholder.setPos(posVec)
            #self.placeholder.setColor(255, 0, 0, 1)
            self.parent.instanceTo(self.placeholder)
            a += aInc
    def DrawCircleXZ(self):
        self.parent = self.loader.loadModel("./Assets/Drones/JulesVerne.obj")
        self.parent.setScale(5)
        a = 0.0
        aInc = 0.2
        R = 50.0

        for i in range(30):
            posVec = (R * math.cos(a), 0, R * math.sin(a))
            self.placeholder = self.render.attachNewNode("Placeholder")
            self.placeholder.setPos(posVec)
            self.placeholder.setColor(0, 0, 255, 1)
            self.parent.instanceTo(self.placeholder)
            a += aInc
    def DrawCircleYZ(self):  
        self.parent = self.loader.loadModel("./Assets/Drones/JulesVerne.obj")
        self.parent.setScale(5)
        a = 0.0
        aInc = 0.2
        R = 50.0

        for i in range(30):
            posVec = (0, R * math.cos(a), R * math.sin(a))
            self.placeholder = self.render.attachNewNode("Placeholder")
            self.placeholder.setPos(posVec)
            self.placeholder.setColor(225, 0, 0, 1)
            self.parent.instanceTo(self.placeholder)
            a += aInc


    def SetupScene(self):
        # Universe setup
        self.Universe = spaceJamClasses.Universe(self.loader, "./Assets/Universe/Universe.x", self.render, 'Universe', "Assets/Universe/space-galaxy.jpg", (0, 0, 0), 15000)

        # Player setup (figure out what to do about traverser)
        self.Player = myPlayer.Player(self.loader, "./Assets/Player/theBorg.x", self.render, 'Player', "Assets/Player/theBorg.jpg", (150, 1500, 67), 5, self.taskMgr, self.render, self.accept, self.traverser)

        # Space station setup
        self.Station = spaceJamClasses.Station(self.loader, "./Assets/SpaceStation1B/spaceStation.x", self.render, 'Station', "Assets/SpaceStation1B/SpaceStation1_Dif2.png", (-1500, 10000, 100), 100)

        # Planet 1 setup
        self.Planet1 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, 'Planet1', "Assets/Planets/planet1.jpg", (350, 5000, 67), 350)

        # Planet 2 setup
        self.Planet2 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, 'Planet2', "Assets/Planets/planet2.jpg", (1500, -2000, 67), 350)

        # Planet 3 setup
        self.Planet3 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, 'Planet3', "Assets/Planets/planet3.jpg", (-1000, -3000, 100), 350)

        # Planet 4 setup
        self.Planet4 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, 'Planet4', "Assets/Planets/planet4.jpg", (-1500, 3000, -67), 350)      

        # Planet 5 setup
        self.Planet5 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, 'Planet5', "Assets/Planets/planet5.jpg", (2500, 5000, -67), 350)

        # Planet 6 setup
        self.Planet6 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, 'Planet6', "Assets/Planets/planet6.jpg", (-650, 5000, 67), 350)

        # Drone pattern setup (don't put anything on planet 1 except for testing purposes) (fix missile problems)
        self.Sentinal1 = spaceJamClasses.Orbiter(self.loader, self.taskMgr, "./Assets/Drones/JulesVerne.obj", self.render, "Drone201", 80.0, "./Assets/Drones/Textures/sh3.jpg", self.Planet1, 500, "MLB", self.Player)
        self.Sentinal2 = spaceJamClasses.Orbiter(self.loader, self.taskMgr, "./Assets/Drones/JulesVerne.obj", self.render, "Drone202", 80.0, "./Assets/Drones/Textures/sh3.jpg", self.Planet2, 500, "Cloud", self.Player)
        self.Sentinal3 = spaceJamClasses.Orbiter(self.loader, self.taskMgr, "./Assets/Drones/JulesVerne.obj", self.render, "Drone203", 80.0, "./Assets/Drones/Textures/sh3.jpg", self.Planet3, 500, "Cloud", self.Player)
        self.Sentinal4 = spaceJamClasses.Orbiter(self.loader, self.taskMgr, "./Assets/Drones/JulesVerne.obj", self.render, "Drone204", 80.0, "./Assets/Drones/Textures/sh3.jpg", self.Planet4, 500, "MLB", self.Player)



app = SpaceJam()
app.run()