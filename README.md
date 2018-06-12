# pychain
> All purpose *blockchain* that can be used for any type of private ledger.

**NOTE**: Still a work in progress.

# My vision for pychain
My vision for this project is to have it be used to enable everyone to use blockchain technology to ensure the entegrity of any process that they are responsible for.

What does that mean? Simply that with deploying *pychain* into your production pipeline, you will be adding an immutable record to any process that you generate. Not only will this make all of your transactions transparent, but will also allow anyone with access to your system to verify the integrity your product.

## Transaction Class
The *Transaction Class* will be very generic so that it can be used in any application. A generic *Transaction* object will have the following features:

* **trans_id**: ID for the *Transaction*
* **user_id**: ID of the user creating the *Transaction*
* **subject_id**: ID of the subject that is affected by the *Transaction*
* **desc**: Description for the *Transaction*
* **payload**: A *json* object with all of the details of the transaction.

## Block Class
The *Block Class* will take your transaction object and add it to the *Blockchain*. The *Block* objects will have the following features:

* **index**: ID for the *Block*
* **timestamp**: Creation date
* **transactions**: A list of *Transaction* objects.
* **previous_hash**: The hash of the previous *Block*
* **hash**: The hash of this *Block*

## Blockchain Class
This class will bring it all together. When a *Blockchain* object is created, you will have the option of loading an existing *Blockchain*. This will allow anyone authorized to be able to join the blockchain at anytime. It will also have the option to add other nodes that are already part of the network. These options by default will not be used, allowing for the *pychain* to be used in a private network without it being to be distributed.

This is what it will be able to do:

* **Instantiate** a new *Blockchain*
* **Generate a Genesis** *Block* for new *Blockchain*
* **Add network nodes**
* **Load** existing *Blockchains*
* **Add new *Blocks*** and **generate new *Block* ID's**
* **Validate *Blocks***
* **Display the *Blockchain*** for review
* **Consensus** of the most current *Blockchain* with all other nodes on the network, if any
