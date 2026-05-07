def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = int(observation.get("grid_width", 8))
    gh = int(observation.get("grid_height", 8))
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < gw and 0 <= py < gh:
                obstacles.add((px, py))
    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    opp_adj = set()
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = ox + dx, oy + dy
            if 0 <= nx < gw and 0 <= ny < gh:
                opp_adj.add((nx, ny))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves.sort()

    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh):
            continue
        if (nx, ny) in obstacles:
            nx, ny = sx, sy  # avoid wasting; engine would keep anyway

        cur_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in opp_adj:
                continue  # likely to be denied soon by opponent
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Race advantage dominates; prefer shorter finish.
            val = (od - sd) * 1000 - sd
            cur_best = val if val > cur_best else cur_best

        # If all resources were skipped as "adjacent", fall back to any.
        if cur_best == -10**18:
            cur_best = -10**18
            for rx, ry in resources:
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                val = (od - sd) * 1000 - sd
                cur_best = val if val > cur_best else cur_best

        # Small anti-collision / anti-lunge: avoid letting opponent get closer.
        if cheb(nx, ny, ox, oy) < cheb(sx, sy, ox, oy):
            cur_best -= 25

        if cur_best > best_val:
            best_val = cur_best
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]