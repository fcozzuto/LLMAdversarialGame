def choose_move(observation):
    w = int(observation.get("grid_width", 8)) or 8
    h = int(observation.get("grid_height", 8)) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    self_ter = set(map(tuple, observation.get("self_territory", []) or []))
    opp_ter = set(map(tuple, observation.get("opponent_territory", []) or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", []) or []))

    resources = list(observation.get("resources", []) or [])
    res_cells = [tuple(r) for r in resources if isinstance(r, (list, tuple)) and len(r) >= 2]

    dirs = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]
    ordered_dirs = dirs

    # Target: if resources exist go to nearest, else go toward center while keeping distance from opponent
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    if res_cells:
        tx, ty = min(res_cells, key=lambda p: abs(p[0]-sx) + abs(p[1]-sy))
        tx, ty = float(tx), float(ty)
    else:
        tx, ty = cx, cy

    best = None
    best_score = -10**18

    for dx, dy in ordered_dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        p = (nx, ny)
        dist_to_target = abs(nx - tx) + abs(ny - ty)
        dist_to_opp = abs(nx - ox) + abs(ny - oy)

        if p in self_ter:
            cell_score = 0.5
        elif p in opp_ter:
            cell_score = 6.0  # capturing/flip
        elif p in unclaimed:
            cell_score = 2.0
        else:
            cell_score = 0.8  # unknown/rarely happens

        # Prefer expansion away from opponent while closing toward target
        score = (cell_score * 3.0) + (-0.9 * dist_to_target) + (0.35 * dist_to_opp)

        # Nudge toward reducing Manhattan distance to target
        cur_dist = abs(sx - tx) + abs(sy - ty)
        if dist_to_target < cur_dist:
            score += 0.8
        elif dist_to_target > cur_dist:
            score -= 0.2

        # Small deterministic bias: slightly favor horizontal/vertical over diagonal
        score -= 0.05 * (abs(dx) == 1 and abs(dy) == 1)

        if score > best_score:
            best_score = score
            best = [int(dx), int(dy)]

    if best is None:
        return [0, 0]
    return best