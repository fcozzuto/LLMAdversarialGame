def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = observation.get("self_role", "pursuer")
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = None

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Prefer moves that lead to immediate capture; otherwise do targeted chase/escape
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in blocked:
            continue
        # Distance metric (Chebyshev works well for 8-neighbor)
        d_cur = max(abs(sx - ox), abs(sy - oy))
        d_new = max(abs(nx - ox), abs(ny - oy))

        if role == "evader":
            # maximize escape progress; bias toward corners away from pursuer
            corner_score = min(nx, w - 1 - nx) + min(ny, h - 1 - ny)
            val = (d_new, corner_score)
            better = (best is None) or (val > best_val)
        else:
            # pursuer: minimize distance; bias toward x/y alignment with opponent
            # (diagonal/axial moves that reduce either coordinate are favored)
            align = - (abs(nx - ox) + abs(ny - oy))
            val = (-d_new, align)
            better = (best is None) or (val > best_val)

        # Immediate capture is always best for pursuer; worst for evader
        if role != "evader" and nx == ox and ny == oy:
            return [dx, dy]
        if role == "evader" and nx == ox and ny == oy:
            continue

        if better:
            best = (dx, dy)
            best_val = val

    if best is not None:
        return [int(best[0]), int(best[1])]

    # Fallback: any move that stays in bounds and avoids obstacles, else stay
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny) and (nx, ny) not in blocked:
            return [int(dx), int(dy)]
    return [0, 0]