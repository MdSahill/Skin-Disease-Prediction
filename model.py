import torch
import torch.nn as nn

class ResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1, use_dropout=False):
        super(ResidualBlock, self).__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, 3, stride, 1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(out_channels, out_channels, 3, 1, 1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        self.use_dropout = use_dropout
        self.dropout = nn.Dropout(0.5) if use_dropout else nn.Identity()

        if in_channels != out_channels or stride != 1:
            self.adjust_identity = nn.Conv2d(in_channels, out_channels, 1, stride, bias=False)
        else:
            self.adjust_identity = None

    def forward(self, x):
        identity = x
        if self.adjust_identity:
            identity = self.adjust_identity(x)

        out = self.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        if self.use_dropout:
            out = self.dropout(out)

        out += identity
        return self.relu(out)

class ResNet(nn.Module):
    def __init__(self, num_classes=22, use_dropout=False):
        super(ResNet, self).__init__()
        self.conv1 = nn.Conv2d(3, 64, 7, 2, 3, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(3, 2, 1)

        self.layer1 = self._make_layer(64, 64, stride=1, use_dropout=use_dropout, blocks=1)
        self.layer2 = self._make_layer(64, 128, stride=2, use_dropout=use_dropout, blocks=1)
        self.layer3 = self._make_layer(128, 256, stride=2, use_dropout=use_dropout, blocks=1)
        self.layer4 = self._make_layer(256, 512, stride=2, use_dropout=use_dropout, blocks=1)

        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(512, num_classes)
        )

    def _make_layer(self, in_c, out_c, stride, use_dropout, blocks):
        layers = [ResidualBlock(in_c, out_c, stride, use_dropout)]
        for _ in range(1, blocks):
            layers.append(ResidualBlock(out_c, out_c, 1, use_dropout))
        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.relu(self.bn1(self.conv1(x)))
        x = self.maxpool(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        return self.fc(x)

def load_model(path='model/resnet_checkpoint.pth', num_classes=22):
    model = ResNet(num_classes=num_classes, use_dropout=True)
    checkpoint = torch.load(path, map_location=torch.device('cpu'))
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    return model
