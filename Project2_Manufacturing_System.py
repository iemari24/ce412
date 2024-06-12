# CMPE412 - Computer Simulation
# Project 2 - Manufacturing System
# Submitted by:
# 20201701021 - Begüm Doğan
# 20191701011 - Kazım Emre Yılmazcan
# Project Supervisors: Dr. Doğan Çörüş


import simpy
import random

class Product:
    def __init__(self, product_id, product_type):
        self.product_id = product_id
        self.product_type = product_type
        self.processing_times = self.set_processing_times()
    
    def set_processing_times(self):
        if self.product_type == 'TypeA':
            return {
                'raw_material': random.uniform(1, 3),
                'machining': random.uniform(4, 6),
                'assembly': random.uniform(2, 4),
                'quality_control': random.uniform(1, 3),
                'packaging': random.uniform(1, 3)
            }
        elif self.product_type == 'TypeB':
            return {
                'raw_material': random.uniform(2, 4),
                'machining': random.uniform(3, 5),
                'assembly': random.uniform(3, 5),
                'quality_control': random.uniform(2, 4),
                'packaging': random.uniform(2, 4)
            }
        else:
            raise ValueError('Unknown product type')

class ManufacturingSystem:
    def __init__(self, env):
        self.env = env
        self.raw_material_handling = simpy.Resource(env, capacity=1)
        self.machining = simpy.Resource(env, capacity=1)
        self.assembly = simpy.Resource(env, capacity=1)
        self.quality_control = simpy.Resource(env, capacity=1)
        self.packaging = simpy.Resource(env, capacity=1)
        self.total_times = {
            'TypeA': {
                'raw_material': 0,
                'machining': 0,
                'assembly': 0,
                'quality_control': 0,
                'packaging': 0
            },
            'TypeB': {
                'raw_material': 0,
                'machining': 0,
                'assembly': 0,
                'quality_control': 0,
                'packaging': 0
            }
        }
        
    def raw_material_process(self, product):
        processing_time = product.processing_times['raw_material']
        yield self.env.timeout(processing_time)
        self.total_times[product.product_type]['raw_material'] += processing_time
        print(f'Product {product.product_id} ({product.product_type}): Raw material handling complete at {self.env.now}')
    
    def machining_process(self, product):
        processing_time = product.processing_times['machining']
        if random.random() < 0.1:  # 10% chance of machine failure
            repair_time = random.uniform(1, 3)
            print(f'Product {product.product_id} ({product.product_type}): Machining failure, repair time {repair_time} at {self.env.now}')
            yield self.env.timeout(repair_time)
        yield self.env.timeout(processing_time)
        self.total_times[product.product_type]['machining'] += processing_time
        print(f'Product {product.product_id} ({product.product_type}): Machining complete at {self.env.now}')
    
    def assembly_process(self, product):
        processing_time = product.processing_times['assembly']
        yield self.env.timeout(processing_time)
        self.total_times[product.product_type]['assembly'] += processing_time
        print(f'Product {product.product_id} ({product.product_type}): Assembly complete at {self.env.now}')
    
    def quality_control_process(self, product):
        processing_time = product.processing_times['quality_control']
        yield self.env.timeout(processing_time)
        self.total_times[product.product_type]['quality_control'] += processing_time
        print(f'Product {product.product_id} ({product.product_type}): Quality control complete at {self.env.now}')
    
    def packaging_process(self, product):
        processing_time = product.processing_times['packaging']
        yield self.env.timeout(processing_time)
        self.total_times[product.product_type]['packaging'] += processing_time
        print(f'Product {product.product_id} ({product.product_type}): Packaging complete at {self.env.now}')

def process_product(env, product, system):
    print(f'Product {product.product_id} ({product.product_type}): Arrived at {env.now}')
    with system.raw_material_handling.request() as request:
        yield request
        yield env.process(system.raw_material_process(product))
    
    with system.machining.request() as request:
        yield request
        yield env.process(system.machining_process(product))
    
    with system.assembly.request() as request:
        yield request
        yield env.process(system.assembly_process(product))
    
    with system.quality_control.request() as request:
        yield request
        yield env.process(system.quality_control_process(product))
    
    with system.packaging.request() as request:
        yield request
        yield env.process(system.packaging_process(product))
    
    print(f'Product {product.product_id} ({product.product_type}): Finished at {env.now}')

env = simpy.Environment()
system = ManufacturingSystem(env)

# Generate a random number of products between 20 and 30
num_products = random.randint(20, 30)
product_types = ['TypeA', 'TypeB']
products = [Product(i, random.choice(product_types)) for i in range(num_products)]

for product in products:
    env.process(process_product(env, product, system))

env.run()

# Output total processing times
print("\nTotal processing times:")
for product_type, times in system.total_times.items():
    total_time = sum(times.values())
    print(f"\n{product_type}:")
    for stage, time in times.items():
        print(f"  {stage}: {time:.2f} min")
    print(f"  Total: {total_time:.2f} min")
