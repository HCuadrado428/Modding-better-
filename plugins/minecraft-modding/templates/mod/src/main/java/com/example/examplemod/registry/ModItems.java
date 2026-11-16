package com.example.examplemod.registry;

import com.example.examplemod.ModIds;
import net.minecraft.world.item.Item;

//? if >=1.21.2 {
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
//?}

/** Items del mod. La creación es común; el registro lo hace cada loader en ExampleMod. */
public final class ModItems {
    public static Item RUBY;

    private ModItems() {
    }

    public static Item create(String name) {
        Item.Properties properties = new Item.Properties();
        //? if >=1.21.2 {
        // Desde 1.21.2 cada item necesita conocer su clave antes de construirse.
        properties = properties.setId(ResourceKey.create(Registries.ITEM, ModIds.id(name)));
        //?}
        return new Item(properties);
    }
}
