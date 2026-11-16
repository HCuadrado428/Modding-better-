package com.example.examplemod;

import com.example.examplemod.registry.ModItems;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/*? if fabric {*/
import net.fabricmc.api.ModInitializer;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
/*?}*/

/*? if forge {*/
/*import net.minecraft.core.registries.Registries;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import net.minecraftforge.registries.RegisterEvent;
*//*?}*/

/*? if neoforge {*/
/*import net.minecraft.core.registries.Registries;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.registries.RegisterEvent;
*//*?}*/

/**
 * Punto de entrada del mod para los tres loaders.
 * El código común vive en otras clases (ModIds, ModItems); aquí solo va el "pegamento" de cada loader.
 */
/*? if neoforge {*/
/*@Mod(ExampleMod.MOD_ID)
*//*?}*/
/*? if forge {*/
/*@Mod(ExampleMod.MOD_ID)
*//*?}*/
public class ExampleMod /*? if fabric {*/ implements ModInitializer /*?}*/ {
    public static final String MOD_ID = "examplemod";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

    /*? if forge {*/
    /*public ExampleMod() {
        IEventBus modBus = FMLJavaModLoadingContext.get().getModEventBus();
        modBus.addListener(ExampleMod::onRegister);
        LOGGER.info("Example Mod cargado en Forge");
    }

    private static void onRegister(RegisterEvent event) {
        event.register(Registries.ITEM, ModIds.id("ruby"), () -> ModItems.RUBY = ModItems.create("ruby"));
    }
    *//*?}*/

    /*? if neoforge {*/
    /*public ExampleMod(IEventBus modBus) {
        modBus.addListener(ExampleMod::onRegister);
        LOGGER.info("Example Mod cargado en NeoForge");
    }

    private static void onRegister(RegisterEvent event) {
        event.register(Registries.ITEM, ModIds.id("ruby"), () -> ModItems.RUBY = ModItems.create("ruby"));
    }
    *//*?}*/

    /*? if fabric {*/
    @Override
    public void onInitialize() {
        ModItems.RUBY = Registry.register(BuiltInRegistries.ITEM, ModIds.id("ruby"), ModItems.create("ruby"));
        LOGGER.info("Example Mod cargado en Fabric");
    }
    /*?}*/
}
