from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import *
from CollideObjectBase import SphereCollideObject
from typing import Callable
from SpaceJamClasses import Missile
from direct.interval.LerpInterval import LerpFunc
from direct.particles.ParticleEffect import ParticleEffect
# Regex module import for string editing.
import re

# Figure out the traversers.
class Player(SphereCollideObject):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float, taskManager: Task, renderer: NodePath, accept: Callable[[str,Callable], None], traverser):
        super(Player, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), 3)
        self.accept = accept
        self.taskManager = taskManager
        self.renderer = renderer
        self.render = parentNode
        self.loader = loader
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)
        
        # SetParticles.
        self.explodeNode = self.render.attachNewNode('ExplosionEffects')        
        base.enableParticles()
        self.explodeEffect = ParticleEffect()
        self.explodeEffect.loadConfig("./Assets/ParticleEffects/basic_xpld_efx.ptf")
        self.explodeEffect.setScale(50)
        self.explodeNode = self.render.attachNewNode('ExplosionEffects') 

        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)

        self.reloadTime = .25
        self.missileDistance = 4000 # Until the missile explodes.
        self.missileBay = 1 # Only one missile in the missile bay to be launched.
        self.taskManager.add(self.CheckIntervals, 'checkMissiles', 34)       

        self.cntExplode = 0
        self.explodeIntervals = {}

        self.traverser = traverser
        
        self.handler = CollisionHandlerEvent()
        self.handler.addInPattern('into')
        self.accept('into', self.HandleInto)

        self.SetKeyBindings()
        self.EnableHUD()
        #Call to control class.
    # Forward and backward thrusts (back thrusts still in development)
    def Thrust(self, keyDown):
        if keyDown:
            self.taskManager.add(self.ApplyThrust, 'forward-thrust')
        else:
            self.taskManager.remove('forward-thrust')
    def ApplyThrust(self, task):
        rate = 15
        trajectory = self.renderer.getRelativeVector(self.modelNode, Vec3.forward())
        trajectory.normalize()
        self.modelNode.setFluidPos(self.modelNode.getPos() + trajectory * rate)
        return Task.cont
    # Back thrust dosen't work if held down, only if mashed.
    def BackThrust(self, keyDown):
        if keyDown:
            self.taskManager.add(self.ApplyBackThrust, 'backward-thrust')
        else:
            self.taskManager.remove('backward-thrust')
    def ApplyBackThrust(self, task):
        rate = 10
        trajectory = self.renderer.getRelativeVector(self.modelNode, Vec3.forward())
        trajectory.normalize()
        self.modelNode.setFluidPos(self.modelNode.getPos() - trajectory * rate)
        return Task.cont       

    # Left and Right turns.
    def LeftTurn(self, keyDown):
        if keyDown:
            self.taskManager.add(self.ApplyLeftTurn, 'left-turn')
        else:
            self.taskManager.remove('left-turn')
    def ApplyLeftTurn(self, task):
        # Rate = turn speed
        rate = 2
        self.modelNode.setH(self.modelNode.getH() + rate)
        return Task.cont          

    def RightTurn(self, keyDown):
        if keyDown:
            self.taskManager.add(self.ApplyRightTurn, 'right-turn')
        else:
            self.taskManager.remove('right-turn')
    def ApplyRightTurn(self, task):
        # Rate = turn speed
        rate = 2
        self.modelNode.setH(self.modelNode.getH() - rate)
        return Task.cont          
 
    # Left and Right rolls.
    def LeftRoll(self, keyDown):
        if keyDown:
            self.taskManager.add(self.ApplyLeftRoll, 'left-roll')
        else:
            self.taskManager.remove('left-roll')
    def ApplyLeftRoll(self, task):
        # Rate = turn speed
        rate = 3
        self.modelNode.setR(self.modelNode.getR() + rate)
        return Task.cont

    def RightRoll(self, keyDown):
        if keyDown:
            self.taskManager.add(self.ApplyRightRoll, 'right-roll')
        else:
            self.taskManager.remove('right-roll')
    def ApplyRightRoll(self, task):
        # Rate = turn speed
        rate = 3
        self.modelNode.setR(self.modelNode.getR() - rate)
        return Task.cont
 
    # Up and Down turns.
    def UpTurn(self, keyDown):
        if keyDown:
            self.taskManager.add(self.ApplyUpTurn, 'turn-up')
        else:
            self.taskManager.remove('turn-up')
    def ApplyUpTurn(self, task):
        rate = 2
        self.modelNode.setP(self.modelNode.getP() + rate)
        return Task.cont    
 
    def DownTurn(self, keyDown):
        if keyDown:
            self.taskManager.add(self.ApplyDownTurn, 'turn-down')
        else:
            self.taskManager.remove('turn-down')
    def ApplyDownTurn(self, task):
        rate = 2
        self.modelNode.setP(self.modelNode.getP() - rate)
        return Task.cont    
    # Resets the camera's orientation when actived.
    def OrienReset(self, keyDown):
        if keyDown:
            self.taskManager.add(self.ApplyOrienReset, 'orien-reset')
        else:
            self.taskManager.remove('orien-reset')
    def ApplyOrienReset(self, task):
        self.modelNode.setP(0)
        self.modelNode.setR(0)
        return Task.cont
    def Fire(self):
        if self.missileBay:
            travRate = self.missileDistance
            aim = self.render.getRelativeVector(self.modelNode, Vec3.forward()) # The direction the spaceship.
            # Normalizing a vecor makes it consistant all the time.
            aim.normalize()

            fireSolution = aim * travRate
            inFront = aim * 150
            travVec = fireSolution + self.modelNode.getPos()
            self.missileBay -= 1
            tag = 'Missile' + str(Missile.missileCount)

            posVec = self.modelNode.getPos() + inFront # Spawn the missile in front of the nose of the ship.

            #Create our missile.
            self.traverser.traverse(self.renderer)
            currentMissile = Missile(self.loader, './Assets/Phaser/phaser.egg', self.render, tag, posVec, 4.0)
            self.traverser.addCollider(currentMissile.collisionNode, self.handler)

            # "fluid = 1" makes collision be checked between the last interval and this interval to make sure there's nothing in-between both check that wasn't hit.
            Missile.Intervals[tag] = currentMissile.modelNode.posInterval(2.0, travVec, startPos = posVec, fluid = 1)
            Missile.Intervals[tag].start()
        else:
            # If we aren't reloading, we want to start reloading.
            if not self.taskManager.hasTaskNamed('reload'):
                print('Initializing Reload...')
                #Call the reload method on no delay.
                self.taskManager.doMethodLater(0, self.Reload, 'reload')
                return Task.cont
    def Reload(self, task):
        if task.time > self.reloadTime:
            self.missileBay += 1
            if self.missileBay > 1:
                self.missileBay = 1
            print("Reload complete.")
            return Task.done
        elif task.time <= self.reloadTime:
            #print("Reload proceeding...")
            return Task.cont
    def CheckIntervals(self, task):
        for i in Missile.Intervals:
            if not Missile.Intervals[i].isPlaying():
                # If its path is done, we get rid of everything to do with that missile.
                Missile.cNodes[i].detachNode()
                Missile.fireModels[i].detachNode()
                del Missile.Intervals[i]
                del Missile.fireModels[i]
                del Missile.cNodes[i]
                del Missile.collisionSolids[i]
                print(i + ' has reached the end of its fire solution.')
                # We break because when things are deleted from a dictionary, we have to refactor the dictionary so we can reuse it. This is because when we delete things, there's a gap at that point.
                break
        return Task.cont

    def EnableHUD(self):
        self.Hud = OnscreenImage(image = "./Assets/Hud/Reticle3b.png", pos = Vec3(0, 0, 0), scale = 0.1)
        self.Hud.setTransparency(TransparencyAttrib.MAlpha)
    
    def HandleInto(self, entry):
        fromNode = entry.getFromNodePath().getName()
        print("fromNode: " + fromNode)
        intoNode = entry.getIntoNodePath().getName()
        print("intoNode: " + intoNode)
        intoPosition = Vec3(entry.getSurfacePoint(self.render))

        tempVar = fromNode.split('_')
        shooter = tempVar[0]
        tempVar = intoNode.split('-')
        tempVar = intoNode.split('_')
        victim = tempVar[0]

        pattern = r'[0-9]'
        strippedString = re.sub(pattern, '', victim)
        if (strippedString == "Drone"):
            print(shooter + ' is DONE.')
            Missile.Intervals[shooter].finish()
            print(victim, ' hit at ', intoPosition)
            self.DroneDestroy(victim, intoPosition)
        else:
            Missile.Intervals[shooter].finish()

    def DroneDestroy(self, hitID, hitPosition):
        nodeID = self.render.find(hitID)
        nodeID.detachNode()

        # Start the explosion.
        self.explodeNode.setPos(hitPosition)
        self.Explode(hitPosition)
    def Explode(self, impactPoint):
        self.cntExplode += 1
        tag = 'particles-' + str(self.cntExplode)

        self.explodeIntervals[tag] = LerpFunc(self.ExplodeLight, fromData = 0, toData = 1, duration = 4.0, extraArgs = [impactPoint])
        self.explodeIntervals[tag].start()
    def ExplodeLight(self, t, explosionPosition):
        if t == 1.0 and self.explodeEffect:
            self.explodeEffect.disable()

        elif t == 0:
            self.explodeEffect.start(self.explodeNode)

    # Keybinds.
    def SetKeyBindings(self):
        # Key bindings for our spaceship's movement.
        self.accept('space', self.Thrust, [1])
        self.accept('space-up', self.Thrust, [0])

        self.accept ('x', self.BackThrust, [1])
        self.accept ('x-up', self.BackThrust, [0])

        self.accept('arrow_left', self.LeftTurn, [1])
        self.accept('arrow_left-up', self.LeftTurn, [0])
        self.accept('a', self.LeftTurn, [1])
        self.accept('a-up', self.LeftTurn, [0])
        
        self.accept('arrow_right', self.RightTurn, [1])
        self.accept('arrow_right-up', self.RightTurn, [0])
        self.accept('d', self.RightTurn, [1])
        self.accept('d-up', self.RightTurn, [0])

        self.accept('q', self.LeftRoll, [1])                     
        self.accept('q-up', self.LeftRoll, [0])

        self.accept('e', self.RightRoll, [1])                     
        self.accept('e-up', self.RightRoll, [0])

        self.accept('arrow_up', self.UpTurn, [1])
        self.accept('arrow_up-up', self.UpTurn, [0])
        self.accept('w', self.UpTurn, [1])
        self.accept('w-up', self.UpTurn, [0])

        self.accept('arrow_down', self.DownTurn, [1])
        self.accept('arrow_down-up', self.DownTurn, [0])
        self.accept('s', self.DownTurn, [1])
        self.accept('s-up', self.DownTurn, [0]) 

        self.accept('r', self.OrienReset, [1])
        self.accept('r-up', self.OrienReset, [0])

        self.accept('f', self.Fire)