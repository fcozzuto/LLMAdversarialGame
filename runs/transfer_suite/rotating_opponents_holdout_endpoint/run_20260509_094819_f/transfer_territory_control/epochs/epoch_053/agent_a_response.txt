def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_set = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_set = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or [])]
    resources = [tuple(p) for p in (observation.get("resources") or [])]

    unclaimed_set = set(unclaimed)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves = [(dx, dy) for dx, dy in moves if abs(dx) <= 1 and abs(dy) <= 1]

    # Targets: prefer unclaimed near center, but also any resource
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    if resources:
        target_list = resources
    else:
        # If unclaimed exists, bias toward those closer to center and farther from opponent
        target_list = unclaimed
        if not target_list:
            target_list = list(opp_set) + list(self_set)  # last resort

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def center_bias(x, y):
        # smaller is better
        return (x - cx) * (x - cx) + (y - cy) * (y - cy)

    # Score next cell: prioritize flipping opponent territory and taking unclaimed, avoid being too close to opponent.
    best = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        val = 0.0
        if (nx, ny) in opp_set:
            val += 45.0
        elif (nx, ny) in unclaimed_set:
            val += 30.0
        elif (nx, ny) in self_set:
            val += 8.0
        else:
            val += 1.0

        # Distance to best local target (prefer closer to a high-value target)
        if target_list:
            local = None
            for tx, ty in target_list[:]:
                if (tx, ty) == (nx, ny):
                    local = 0
                    break
                d = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
                # prefer near center targets and away from opponent
                d2 = d + 0.2 * center_bias(tx, ty) + 0.35 * manh(tx, ty, ox, oy)
                if local is None or d2 < local:
                    local = d2
            val += 12.0 / (1.0 + (local if local is not None else 0.0))

        # Opponent proximity penalty (don't allow easy sweep)
        dop = manh(nx, ny, ox, oy)
        val -= 6.5 / (1.0 + dop)

        # Slight preference toward staying/advancing to unclaimed
        if (nx, ny) in unclaimed_set:
            val += 3.0

        # Deterministic tie-break: lowest dx, then lowest dy
        if best is None or val > best or (abs(val - best) < 1e-9 and (dx, dy) < best_move):
            best = val
            best_move = (dx, dy)

    dx, dy = best_move
    if (sx + dx, sy + dy) in obstacles or not (0 <= sx + dx < w and 0 <= sy + dy < h):
        return [0, 0]
    return [int(dx), int(dy)]