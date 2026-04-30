def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    # Moves: 8-neighborhood + stay
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)
    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy
    def pick_target():
        if not resources:
            return None
        best = None
        best_val = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            md = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            val = (od - md) * 2 + (-(dist2(sx, sy, rx, ry))) // 2
            # Encourage moving to resources closer to me
            val -= (md // 2)
            if val > best_val:
                best_val = val
                best = (rx, ry)
        return best
    target = pick_target()
    if target is None:
        # No resources: drift toward center to reduce being trapped
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        best = (0, 0)
        bestv = 10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = dist2(nx, ny, tx, ty)
            if v < bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]
    tx, ty = target
    # Evaluate candidate moves: prefer moving closer to target; avoid obstacles; slight anti-collision heuristic
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_d = dist2(nx, ny, tx, ty)
        cur_d = dist2(sx, sy, tx, ty)
        rel_progress = cur_d - my_d
        # Discourage moving into/near opponent
        opp_d = dist2(nx, ny, ox, oy)
        opp_pen = 0
        if opp_d <= 1:
            opp_pen = -10
        # Prefer moves that also improve opponent disadvantage for this target
        opp_to_target = dist2(ox, oy, tx, ty)
        # Estimate how opponent might be positioned: use current opp_to_target only (deterministic)
        score = rel_progress * 3 + (opp_d - opp_to_target) // 2 + opp_pen
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]