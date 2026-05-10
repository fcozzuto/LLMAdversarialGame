def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", []) or []
    obstacle_set = {(int(x), int(y)) for x, y in obstacles}

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    if "evad" in sr:
        role = "evader"
    elif "evad" in orr:
        role = "pursuer"
    else:
        role = "pursuer"

    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_dx, best_dy = 0, 0
    best_val = None

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    for dx, dy in deltas:
        nx = clamp(sx + dx, 0, w - 1)
        ny = clamp(sy + dy, 0, h - 1)
        if (nx, ny) in obstacle_set:
            continue

        dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        on_top = (nx == ox and ny == oy)

        # Mild obstacle-aware term: prefer staying with more free adjacent cells
        free_adj = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                tx = nx + adx
                ty = ny + ady
                if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obstacle_set:
                    free_adj += 1

        if role == "pursuer":
            val = (-1000000 if on_top else 0) - dist2 + 0.01 * free_adj
        else:
            val = (1000000 if on_top else 0) + dist2 + 0.01 * free_adj

        if best_val is None or val > best_val or (val == best_val and (dx, dy) < (best_dx, best_dy)):
            best_val = val
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]