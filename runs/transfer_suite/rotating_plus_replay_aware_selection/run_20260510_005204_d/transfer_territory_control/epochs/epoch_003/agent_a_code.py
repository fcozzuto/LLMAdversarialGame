def choose_move(observation):
    sx, sy = observation["self_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    self_territory = set(tuple(p) for p in observation.get("self_territory", []))
    opp_territory = set(tuple(p) for p in observation.get("opponent_territory", []))
    unclaimed = set(tuple(p) for p in observation.get("unclaimed_cells", []))
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Decide objective: catch up by pressuring opponent; otherwise expand unclaimed.
    if observation.get("self_territory_count", len(self_territory)) <= observation.get("opponent_territory_count", len(opp_territory)):
        targets = list(opp_territory) if opp_territory else list(unclaimed)
    else:
        targets = list(unclaimed) if unclaimed else list(opp_territory)

    if not targets:
        return [0, 0]

    # Pick deterministic target: nearest; tie-break toward advancing (smaller y first for determinism).
    # For opposite corners, this biases toward centerline expansion.
    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    target = min(targets, key=lambda c: (dist2((sx, sy), c), c[1], c[0]))

    tx, ty = target

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        # Immediate gain heuristic:
        # - entering unclaimed likely grants +1
        # - entering opponent territory likely flips and grants +1
        # - staying in own territory yields no immediate cell gain
        immediate = 0
        if cell in unclaimed or cell in opp_territory:
            immediate = 1
        elif cell in self_territory:
            immediate = 0

        # Frontier pressure: move closer to target, prefer progress toward it
        d_curr = dist2((sx, sy), (tx, ty))
        d_next = dist2((nx, ny), (tx, ty))
        progress = d_curr - d_next

        # Slightly prefer moves that are not too "sideways" (deterministic shaping)
        align = -abs(nx - tx) - abs(ny - ty)

        score = 5 * immediate + 2 * progress + 0.001 * align

        # Deterministic tie-break: prefer (dx,dy) order as listed
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]