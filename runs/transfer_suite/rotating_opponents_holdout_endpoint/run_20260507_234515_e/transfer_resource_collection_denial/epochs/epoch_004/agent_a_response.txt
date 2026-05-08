def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    if not resources:
        return [0, 0]

    best = None
    for rx, ry in resources:
        dself = (rx - sx) * (rx - sx) + (ry - sy) * (ry - sy)
        dopp = (rx - ox) * (rx - ox) + (ry - oy) * (ry - oy)
        # Prefer resources where we are closer than opponent; tie-break toward smaller self distance, then position
        key = (-(dopp - dself), dself, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    dx = sign(tx - sx)
    dy = sign(ty - sy)

    moves = [(0, 0), (dx, dy), (dx, 0), (0, dy), (-dx, dy), (dx, -dy), (-dx, 0), (0, -dy),
             (dx if dx != 0 else 1, dy if dy != 0 else 1), (-dx if dx != 0 else -1, dy if dy != 0 else 1)]
    # Deduplicate while preserving order
    seen = set()
    uniq = []
    for m in moves:
        if m not in seen:
            seen.add(m)
            uniq.append(m)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    # Score each move: closer to target, don't step into obstacle, and prefer moves that keep/restore lead
    best_move = (0, 0)
    best_score = None
    for ddx, ddy in uniq:
        nx, ny = sx + ddx, sy + ddy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        d_to_target = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
        dself_old = (tx - sx) * (tx - sx) + (ty - sy) * (ty - sy)
        # Lead after move: smaller opponent distance minus our distance (bigger is better)
        # Use target's resource comparison only (deterministic, cheap)
        dopp = (tx - ox) * (tx - ox) + (ty - oy) * (ty - oy)
        dself = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
        lead = dopp - dself

        # Small penalty for not making progress to avoid dithering
        progress_pen = 0 if d_to_target < dself_old else 4

        # Deterministic tie-break by move preference toward desired direction then toward lower dx,dy
        dir_pref = 0 if (ddx == dx or dx == 0) and (ddy == dy or dy == 0) else 3

        score = (-lead, d_to_target, progress_pen + dir_pref, ddx, ddy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (ddx, ddy)

    # If all safe moves invalid (should be rare), allow staying
    return [int(best_move[0]), int(best_move[1])]