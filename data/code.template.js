// State management.
let selectedIcon = null;
let showControlPoints = false;
let showGrid = false;
let iconSize = 512;

// Icon data.
const icons = %ICONS_DATA%;

// Function to extract control points.
function extractControlPoints(pathData) {
    const points = [];
    const commands = pathData.match(/[MLHVCSQTAZmlhvcsqtaz]|[+-]?\d*\.?\d+/g) || [];

    let x = 0, y = 0;
    let prevX = 0, prevY = 0;
    let controlX = 0, controlY = 0;

    for (let i = 0; i < commands.length; i++) {
        const cmd = commands[i];

        if (cmd.match(/[MLHVCSQTAZmlhvcsqtaz]/)) {
            const command = cmd.toUpperCase();

            // Handle different commands
            switch (command) {
                case "M":
                    x = parseFloat(commands[++i]);
                    y = parseFloat(commands[++i]);
                    points.push({ x, y, type: "move" });
                    break;
                case "L":
                    x = parseFloat(commands[++i]);
                    y = parseFloat(commands[++i]);
                    points.push({ x, y, type: "line" });
                    break;
                case "C":
                    const x1 = parseFloat(commands[++i]);
                    const y1 = parseFloat(commands[++i]);
                    const x2 = parseFloat(commands[++i]);
                    const y2 = parseFloat(commands[++i]);
                    x = parseFloat(commands[++i]);
                    y = parseFloat(commands[++i]);
                    points.push(
                        { x: x1, y: y1, type: "control", connectsTo: "start" },
                        { x: x2, y: y2, type: "control", connectsTo: "end" },
                        { x, y, type: "curve" }
                    );
                    break;
                case "S":
                    const x2s = parseFloat(commands[++i]);
                    const y2s = parseFloat(commands[++i]);
                    x = parseFloat(commands[++i]);
                    y = parseFloat(commands[++i]);
                    // Calculate reflection of previous control point.
                    const prevControlX = 2 * x - controlX;
                    const prevControlY = 2 * y - controlY;
                    points.push(
                        { x: prevControlX, y: prevControlY, type: "control", connectsTo: "start" },
                        { x: x2s, y: y2s, type: "control", connectsTo: "end" },
                        { x, y, type: "curve" }
                    );
                    break;
                case "Q":
                    const qx1 = parseFloat(commands[++i]);
                    const qy1 = parseFloat(commands[++i]);
                    x = parseFloat(commands[++i]);
                    y = parseFloat(commands[++i]);
                    points.push(
                        { x: qx1, y: qy1, type: "control", connectsTo: "both" },
                        { x, y, type: "quadratic" }
                    );
                    break;
                case "T":
                    x = parseFloat(commands[++i]);
                    y = parseFloat(commands[++i]);
                    // Calculate reflection of previous control point.
                    const qPrevControlX = 2 * x - controlX;
                    const qPrevControlY = 2 * y - controlY;
                    points.push(
                        { x: qPrevControlX, y: qPrevControlY, type: "control", connectsTo: "both" },
                        { x, y, type: "quadratic" }
                    );
                    break;
                case "Z":
                    points.push({ x, y, type: "close" });
                    break;
                case "A":
                    const rx = parseFloat(commands[++i]);
                    const ry = parseFloat(commands[++i]);
                    const xAxisRotation = parseFloat(commands[++i]);
                    const largeArcFlag = parseFloat(commands[++i]);
                    const sweepFlag = parseFloat(commands[++i]);
                    x = parseFloat(commands[++i]);
                    y = parseFloat(commands[++i]);

                    // For arcs, we'll only add the start and end points.
                    const startX = prevX;
                    const startY = prevY;

                    // Add the start point if it's not already added.
                    if (points.length === 0 || points[points.length - 1].type !== "move") {
                        points.push({ x: startX, y: startY, type: "arc-start" });
                    }

                    // Add the end point.
                    points.push({ x, y, type: "arc-end" });
                    break;
            }

            prevX = x;
            prevY = y;
            if (command === "C" || command === "S" || command === "Q" || command === "T") {
                controlX = x;
                controlY = y;
            }
        }
    }
    return points;
}

// Function to draw control points.
function drawControlPoints(points) {
    const layer = document.getElementById("controlPointsLayer");
    layer.innerHTML = "";

    if (!showControlPoints) return;

    // Draw all points first.
    points.forEach(point => {
        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        if (point.type === "control") {
            circle.setAttribute("class", "control-point");
        } else if (point.type === "arc-start" || point.type === "arc-end") {
            circle.setAttribute("class", "curve-point");
        } else {
            circle.setAttribute("class", point.type === "control" ? "control-point" : "curve-point");
        }
        circle.setAttribute("cx", point.x);
        circle.setAttribute("cy", point.y);
        layer.appendChild(circle);
    });

    // Draw control lines for Bezier curves.
    for (let i = 0; i < points.length; i++) {
        const point = points[i];
        if (point.type === "control") {
            if (point.connectsTo === "both") {
                // For quadratic curves, connect to both previous and next points.
                const prevPoint = points[i - 1];
                const nextPoint = points[i + 1];
                if (prevPoint && prevPoint.type !== "control") {
                    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
                    line.setAttribute("class", "control-line");
                    line.setAttribute("x1", point.x);
                    line.setAttribute("y1", point.y);
                    line.setAttribute("x2", prevPoint.x);
                    line.setAttribute("y2", prevPoint.y);
                    layer.appendChild(line);
                }
                if (nextPoint && nextPoint.type !== "control") {
                    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
                    line.setAttribute("class", "control-line");
                    line.setAttribute("x1", point.x);
                    line.setAttribute("y1", point.y);
                    line.setAttribute("x2", nextPoint.x);
                    line.setAttribute("y2", nextPoint.y);
                    layer.appendChild(line);
                }
            } else if (point.connectsTo === "arc-start" || point.connectsTo === "arc-end") {
                // Skip control lines for arcs.
                continue;
            } else {
                // For cubic curves, connect to either start or end point.
                const targetIndex = point.connectsTo === "start" ? i - 1 : i + 1;
                const targetPoint = points[targetIndex];
                if (targetPoint && targetPoint.type !== "control") {
                    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
                    line.setAttribute("class", "control-line");
                    line.setAttribute("x1", point.x);
                    line.setAttribute("y1", point.y);
                    line.setAttribute("x2", targetPoint.x);
                    line.setAttribute("y2", targetPoint.y);
                    layer.appendChild(line);
                }
            }
        }
    }
}

// Function to draw grid.
function drawGrid(svg, scale) {
    const gridGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
    gridGroup.setAttribute("class", "grid-elements");

    // Draw vertical lines.
    for (let x = 1; x <= 15; x++) {
        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("class", "grid-line");
        line.setAttribute("x1", x);
        line.setAttribute("y1", 1 - 0.2);
        line.setAttribute("x2", x);
        line.setAttribute("y2", 15 + 0.2);
        line.setAttribute("stroke-width", 0.02 / scale);
        gridGroup.appendChild(line);
    }

    // Draw horizontal lines.
    for (let y = 1; y <= 15; y++) {
        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("class", "grid-line");
        line.setAttribute("x1", 1 - 0.2);
        line.setAttribute("y1", y);
        line.setAttribute("x2", 15 + 0.2);
        line.setAttribute("y2", y);
        line.setAttribute("stroke-width", 0.02 / scale);
        gridGroup.appendChild(line);
    }
    return gridGroup;
}

// Update icon style.
function updateIconStyle() {

    const svg = document.getElementById("previewSvg");
    if (!svg) return;

    // Update SVG size.
    svg.style.width = `${iconSize}px`;
    svg.style.height = `${iconSize}px`;
    const scale = iconSize / 512;

    // Clear the SVG.
    svg.innerHTML = "";

    // Add the path.
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", selectedIcon.path);
    path.style.fill = "currentColor";
    path.style.stroke = "currentColor";

    if (showControlPoints && iconSize > 64) {
        path.style.fillOpacity = "0.05";
        path.style.strokeWidth = `${0.05 / scale}px`;
    } else {
        path.style.fillOpacity = "1";
        path.style.strokeWidth = "0px";
    }
    svg.appendChild(path);

    // If showing grid, add it first (so it's behind the icon).
    if (showGrid && iconSize > 64) {
        const gridGroup = drawGrid(svg, scale);
        svg.insertBefore(gridGroup, svg.firstChild);
    }

    // If showing control points, add them to the same SVG.
    if (showControlPoints && iconSize > 64) {
        const points = extractControlPoints(selectedIcon.path);

        // Create a group for control elements to ensure they're drawn on top.
        const controlGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
        controlGroup.setAttribute("class", "control-elements");

        // Draw all points.
        points.forEach(point => {
            const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            var class_name;
            if (point.type === "control") {
                class_name = "control-point";
            } else if (point.type === "arc-start" || point.type === "arc-end") {
                class_name = "curve-point";
            } else {
                class_name = point.type === "control" ? "control-point" : "curve-point";
            }
            circle.setAttribute("class", class_name);
            if (class_name === "control-point") {
                circle.setAttribute("r", 0.00 / scale);
            } else if (class_name === "curve-point") {
                circle.setAttribute("r", 0.08 / scale);
            }
            circle.setAttribute("cx", point.x);
            circle.setAttribute("cy", point.y);
            controlGroup.appendChild(circle);
        });

        // Draw control lines for Bezier curves.
        for (let i = 0; i < points.length; i++) {
            const point = points[i];
            if (point.type === "control") {
                if (point.connectsTo === "both") {
                    // For quadratic curves, connect to both previous and next points.
                    const prevPoint = points[i - 1];
                    const nextPoint = points[i + 1];
                    if (prevPoint && prevPoint.type !== "control") {
                        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
                        line.setAttribute("class", "control-line");
                        line.setAttribute("x1", point.x);
                        line.setAttribute("y1", point.y);
                        line.setAttribute("x2", prevPoint.x);
                        line.setAttribute("y2", prevPoint.y);
                        line.setAttribute("stroke-width", 0.02 / scale);
                        controlGroup.appendChild(line);
                    }
                    if (nextPoint && nextPoint.type !== "control") {
                        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
                        line.setAttribute("class", "control-line");
                        line.setAttribute("x1", point.x);
                        line.setAttribute("y1", point.y);
                        line.setAttribute("x2", nextPoint.x);
                        line.setAttribute("y2", nextPoint.y);
                        line.setAttribute("stroke-width", 0.02 / scale);
                        controlGroup.appendChild(line);
                    }
                } else if (point.connectsTo === "arc-start" || point.connectsTo === "arc-end") {
                    // Skip control lines for arcs.
                    continue;
                } else {
                    // For cubic curves, connect to either start or end point.
                    const targetIndex = point.connectsTo === "start" ? i - 1 : i + 1;
                    const targetPoint = points[targetIndex];
                    if (targetPoint && targetPoint.type !== "control") {
                        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
                        line.setAttribute("class", "control-line");
                        line.setAttribute("x1", point.x);
                        line.setAttribute("y1", point.y);
                        line.setAttribute("x2", targetPoint.x);
                        line.setAttribute("y2", targetPoint.y);
                        line.setAttribute("stroke-width", 0.02 / scale);
                        controlGroup.appendChild(line);
                    }
                }
            }
        }
        svg.appendChild(controlGroup);
    }
}

// Select and display icon.
function selectIcon(name) {
    selectedIcon = icons[name];
    if (!selectedIcon) return;

    // Update URL hash.
    window.location.hash = name;

    // Update UI.
    document.querySelectorAll(".icon-item").forEach((item) => {
        item.classList.toggle("selected", item.dataset.name === name);
    });

    // Update metadata.
    document.getElementById("iconName").textContent = selectedIcon.capitalized_name;

    // Update identifier, add invisible break after every "_" in identifier.
    document.getElementById("iconIdentifier").innerHTML = selectedIcon.identifier.replace(/_/g, "_<wbr>");

    // Update tags.
    const tagsContainer = document.getElementById("iconTags");
    tagsContainer.innerHTML = "";
    selectedIcon.tags.forEach((tag) => {
        const tagElement = document.createElement("span");
        tagElement.className = "tag";
        tagElement.textContent = tag;
        tagsContainer.appendChild(tagElement);
    });

    updateIconStyle();
}

// Function to create downloadable SVG.
function createDownloadableSVG() {
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("xmlns", "http://www.w3.org/2000/svg");
    svg.setAttribute("width", "16");
    svg.setAttribute("height", "16");

    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", selectedIcon.path);
    path.setAttribute("fill", "#000000");
    svg.appendChild(path);

    return new XMLSerializer().serializeToString(svg);
}

// Function to download SVG.
function downloadSVG() {
    if (!selectedIcon) return;

    const svgContent = createDownloadableSVG();
    const blob = new Blob([svgContent], { type: "image/svg+xml" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `roentgen_${selectedIcon.identifier}.svg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// Function to get current icon index and navigate to next/previous icon.
function navigateIcons(direction) {
    console.log("navigateIcons", direction);
    if (!selectedIcon) return;

    // Get all icon items and current index
    const iconItems = Array.from(document.querySelectorAll(".icon-item"));
    const currentIndex = iconItems.findIndex(item => item.dataset.name === selectedIcon.identifier);

    if (currentIndex === -1) return;

    // Calculate new index based on direction
    let newIndex;
    if (direction === "next") {
        newIndex = (currentIndex + 1) % iconItems.length;
    } else {
        newIndex = (currentIndex - 1 + iconItems.length) % iconItems.length;
    }

    // Select the new icon
    selectIcon(iconItems[newIndex].dataset.name);
}

// Function to toggle grid visibility.
function toggleGrid() {
    const gridCheckbox = document.getElementById("toggleGrid");
    gridCheckbox.checked = !gridCheckbox.checked;
    showGrid = gridCheckbox.checked;
    updateIconStyle();
}

// Function to toggle control points visibility.
function toggleControlPoints() {
    const controlPointsCheckbox = document.getElementById("toggleControlPoints");
    controlPointsCheckbox.checked = !controlPointsCheckbox.checked;
    showControlPoints = controlPointsCheckbox.checked;
    updateIconStyle();
}

// Function to filter icons based on search query.
function filterIcons(query) {
    query = query.toLowerCase();
    const iconItems = document.querySelectorAll(".icon-item");
    
    iconItems.forEach(item => {
        const icon = icons[item.dataset.name];
        if (!icon) return;

        // Search in name, identifier, and tags
        const searchText = [
            icon.name,
            icon.identifier,
            ...icon.tags
        ].join(" ").toLowerCase();

        const isVisible = searchText.includes(query);
        item.style.display = isVisible ? "" : "none";
    });

    // If current icon is hidden, select the first visible icon
    const selectedItem = document.querySelector(".icon-item.selected");
    if (selectedItem && selectedItem.style.display === "none") {
        const firstVisible = document.querySelector(".icon-item:not([style*='display: none'])");
        if (firstVisible) {
            selectIcon(firstVisible.dataset.name);
        }
    }
}

// Initialize event listeners.
document.addEventListener('DOMContentLoaded', () => {
    // Add search input handler
    const searchInput = document.getElementById("iconSearch");
    searchInput.addEventListener("input", (e) => {
        filterIcons(e.target.value);
    });

    // Add click handlers to icon items.
    document.querySelectorAll(".icon-item").forEach((item) => {
        item.addEventListener("click", () => selectIcon(item.dataset.name));
    });

    // Add click handler to control points toggle.
    document.getElementById("toggleControlPoints").addEventListener("change", (e) => {
        showControlPoints = e.target.checked;
        updateIconStyle();
    });

    // Add click handler to download button.
    document.getElementById("downloadIcon").addEventListener("click", downloadSVG);

    // Add input handler to size slider.
    const sizeSlider = document.getElementById("sizeSlider");
    sizeSlider.addEventListener("input", (e) => {
        iconSize = parseInt(e.target.value);
        document.querySelector(".size-value").textContent = `${iconSize}px`;
        updateIconStyle();
    });

    // Add click handler to grid toggle.
    document.getElementById("toggleGrid").addEventListener("change", (e) => {
        showGrid = e.target.checked;
        updateIconStyle();
    });

    // Add keyboard event listener for arrow keys and other shortcuts.
    document.addEventListener('keydown', (e) => {
        // Only handle shortcuts if no input element is focused
        if (document.activeElement.tagName === 'INPUT' && document.activeElement.id !== 'iconSearch') return;
        
        switch (e.key.toLowerCase()) {
            case 'arrowleft':
                navigateIcons('prev');
                break;
            case 'arrowright':
                navigateIcons('next');
                break;
            case 'g':
                toggleGrid();
                break;
            case 'p':
                toggleControlPoints();
                break;
        }
    });

    // Handle hash changes
    window.addEventListener('hashchange', () => {
        const iconName = window.location.hash.slice(1); // Remove the # symbol
        if (iconName && icons[iconName]) {
            selectIcon(iconName);
        }
    });

    // Select icon from URL hash or default to first icon
    const iconName = window.location.hash.slice(1);
    if (iconName && icons[iconName]) {
        selectIcon(iconName);
    } else {
        selectIcon("camp");
    }

    // Set initial size value.
    document.querySelector(".size-value").textContent = `${iconSize}px`;
}); 