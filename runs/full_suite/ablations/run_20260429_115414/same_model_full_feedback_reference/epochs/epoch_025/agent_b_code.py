def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                resources.append((x, y))
    seen = set()
    res = []
    for r in resources:
        if r not in seen:
            seen.add(r)
            res.append(r)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_d = None
    best = (0, 0)

    if res:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            self_d = min(man(nx, ny, rx, ry) for rx, ry in res)
            opp_d = min(man(ox, oy, rx, ry) for rx, ry in res)
            self_after = min(man(nx, ny, rx, ry) for rx, ry in res)
            # Prioritize gaining resource race; also discourage moves that let opponent be closer after us.
            score = (opp_d - self_after) * 1000 - self_after
            # Mild tie-break: prefer moves that keep away from opponent when not racing.
            score += -man(nx, ny, ox, oy) // 4
            # Slight preference for progressing toward nearest resource direction.
            score += -abs(nx - ox) // 50
            if best_d is None or score > best_d:
                best_d = score
                best = (dx, dy)
    else:
        cx, cy = (W - 1) // 2, (H - 1) // 2
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            self_center = man(nx, ny, cx, cy)
            opp_dist = man(nx, ny, ox, oy)
            score = -self_center + opp_dist // 2
            if best_d is None or score > best_d:
                best_d = score
                best = (dx, dy)

    return [int(best[0]), int(best[1])]