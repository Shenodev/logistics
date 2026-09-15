<template>
  <main class="flex-1 flex items-center justify-center p-8">
    <Card class="w-full max-w-md bg-card border-border">
      <CardHeader>
        <CardTitle class="text-2xl font-heading">Logistics Control</CardTitle>
        <CardDescription>Nuxt runtime config + subdomain routing</CardDescription>
      </CardHeader>
      <CardContent class="space-y-4">
        <Badge class="bg-primary text-primary-foreground">Deep Slate x Electric Cyan</Badge>
        <Input class="bg-secondary border-border" type="text" placeholder="Search shipment..." />
        <div class="flex items-center gap-3">
          <Avatar class="bg-cyan-900 text-cyan-200">
            <AvatarFallback>LC</AvatarFallback>
          </Avatar>
          <div class="flex flex-col gap-2">
            <Separator class="bg-border" />
            <Skeleton class="h-4 w-32 bg-muted" />
          </div>
        </div>
      </CardContent>
      <CardFooter class="flex justify-between">
        <Button variant="secondary" class="bg-secondary text-secondary-foreground">Back</Button>
        <Button class="bg-primary text-primary-foreground">Track</Button>
      </CardFooter>
    </Card>
  </main>
</template>