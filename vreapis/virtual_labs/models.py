from django.db import models

class VLProfile(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    display_name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    image = models.CharField(max_length=100)

    def __str__(self):
            return self.display_name

    class Meta:

        verbose_name = "VL Profile"
        verbose_name_plural = "VL Profiles"


class VM(models.Model):

    CHOICES_ASSIGN_PUBLIC_IP = (
        ('yes', 'Yes'),
        ('no', 'No')
    )

    CHOICES_ROLE = (
        ('master', 'Master'),
        ('worker', 'Worker')
    )

    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=CHOICES_ROLE)
    name = models.CharField(max_length=100)
    assign_public_ip = models.CharField(max_length=3, choices=CHOICES_ASSIGN_PUBLIC_IP)
    disk_size = models.CharField(max_length=5)
    mem_size = models.CharField(max_length=5)
    num_cores = models.IntegerField(default=2)
    user_name = models.CharField(max_length=100)

    def __str__(self):
            return self.name

    class Meta:

        verbose_name = "Virtual Machine"


class Topology(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    domain = models.CharField(max_length=100)
    provider = models.CharField(max_length=100)

    def __str__(self):
            return self.provider

    class Meta:

        verbose_name = "Topology"
        verbose_name_plural = "Topologies"


class SDIAProvision(models.Model):

    name = models.CharField(max_length=100, default='')
    vms = models.ManyToManyField(VM)
    topology = models.ForeignKey(Topology, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name
    
    class Meta:

        verbose_name = "SDIA Provision"


class VirtualLab(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    provision = models.ForeignKey(SDIAProvision, on_delete=models.SET_NULL, null=True)
    profiles = models.ManyToManyField(VLProfile)

    def __str__(self):
            return self.title

    class Meta:

        verbose_name = "Virtual Lab"


class KeyCloakAuth(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    issuer = models.CharField(max_length=100)
    client_id = models.CharField(max_length=100)
    client_secret = models.CharField(max_length=100)
    realm_name = models.CharField(max_length=100)

    def __str__(self):
            return self.issuer

    class Meta:

        verbose_name = "KeyCloak Auth"