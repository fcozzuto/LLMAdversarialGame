def choose_move(observation):
    # Defensive access with defaults
    # Try common fields for a 2D grid agent: "pos", "agent_pos", "self_pos", "location"
    # We'll determine a target from a few basic heuristics and return a safe move.
    x = observation.get("x", observation.get("pos", {}).get("x", 0))
    y = observation.get("y", observation.get("pos", {}).get("y", 0))
    # Build a simple local view if available
    grid = observation.get("grid", observation.get("local_view", [[0, 0, 0]]))
    # Flatten neighbor indicators if provided
    nearby = []
    if isinstance(grid, list) and grid:
        try:
            # Try to extract a 3x3 neighborhood around current position
            for dy in (-1, 0, 1):
                row = grid[y + dy] if isinstance(grid, list) and len(grid) > 0 else []
                if isinstance(row, list):
                    for dx in (-1, 0, 1):
                        if isinstance(row, list) and len(row) > x + dx:
                            nearby.append(row[x + dx])
        except Exception:
            nearby = []
    # Define safe default move: try to stay still
    dx = 0
    dy = 0

    # Simple heuristics:
    # 1) If there is an opponent/resource in immediate vicinity, move away from threats (simulate evasive)
    # 2) If there is a resource nearby (positive value), move toward it
    # 3) Otherwise stay or explore: move randomly among -1,0,1 handled deterministically
    # Since we must be deterministic and not use randomness, pick based on observed signals.

    # Detect threats/resources in the 8-neighborhood from nearby data if available
    threat = None
    resource = None
    if isinstance(nearby, list) and nearby:
        # heuristically interpret non-zero as something of interest
        # first pass: look for high positive values as resources, negative as threats
        for idx, val in enumerate(nearby):
            if val is None:
                continue
            if isinstance(val, (int, float)):
                if val > 0:
                    resource = val
                    break
                if val < 0 and threat is None:
                    threat = val

    # Map index to direction: we don't have a full mapping without grid coords.
    # Use a simple rule: prefer moving towards resource if detected by nearest positive in neighborhood,
    # else if threat detected, move away from center (0,0) by pushing away from origin of neighborhood.
    if resource is not None:
        # Move towards resource: attempt to increment toward (0,0) in neighborhood indexing
        # We'll bias toward (dx,dy) = (-1,0,1) by assuming index order corresponds to grid around current pos.
        # Simpler: choose a fixed direction that tends toward positive dx, dy if possible: dx=1, dy=1
        dx, dy = 1, 1
    elif threat is not None:
        # Move away from threat: choose opposite direction
        dx, dy = -1, -1
    else:
        # Default exploration: move in a deterministic small pattern: try to move right then down
        if observation.get("turn", 0) % 2 == 0:
            dx, dy = 1, 0
        else:
            dx, dy = 0, 1

    # Clip to allowed range
    if dx not in (-1, 0, 1): dx = 0
    if dy not in (-1, 0, 1): dy = 0
    return [dx, dy]
