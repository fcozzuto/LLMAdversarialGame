def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    opp = set((int(t[0]), int(t[1])) for t in (observation.get("opponent_territory") or []) if t and len(t) >= 2)
    unclaimed = [(int(c[0]), int(c[1])) for c in (observation.get("unclaimed_cells") or []) if c and len(c) >= 2]
    if not unclaimed:
        unclaimed = []

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    # Deterministic target selection: first try counterclaiming (enter opponent territory), else expand to unclaimed.
    target_list = []
    if opp:
        # Choose the closest opponent cell, tie-break by being "more reachable" from our side.
        target_list = list(opp)
        target_list.sort(key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))
        target = target_list[0]
    elif unclaimed:
        target_list = unclaimed
        # Prefer cells that also tend to swing control (closer to opponent corner).
        oc = observation.get("opponent_position", [w - 1, h - 1])
        ox, oy = int(oc[0]), int(oc[1])
        target_list.sort(key=lambda c: (abs(c[0] - sx) + abs(c[1] - sy), - (abs(c[0] - ox) + abs(c[1] - oy)), c[0], c[1]))
        target = target_list[0]
    else:
        return [0, 0]

    tx, ty = int(target[0]), int(target[1])

    best = (0, 0)
    best_val = None
    # Heuristic: entering opponent territory is best; otherwise chase target; avoid obstacles and reduce risk of oscillation via preference to change.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        val = 0
        if (nx, ny) in opp:
            val += 100000  # strong preference to counterclaim
        # Main chase component
        dist = abs(nx - tx) + abs(ny - ty)
        val -= dist * 100
        # Mild bias to move rather than stay unless already optimal
        val -= 5 if (dx == 0 and dy == 0) else 0
        # Favor reducing distance vs opponent when counterclaiming is not possible
        if not opp:
            oc = observation.get("opponent_position", [w - 1, h - 1])
            ox, oy = int(oc[0]), int(oc[1])
            val -= (abs(nx - ox) + abs(ny - oy)) * 2

        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]