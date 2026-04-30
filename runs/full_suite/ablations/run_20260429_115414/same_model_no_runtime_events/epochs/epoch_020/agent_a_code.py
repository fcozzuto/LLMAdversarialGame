def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def bfs(start):
        x0, y0 = start
        if (x0, y0) in obs:
            return {}
        dist = {(x0, y0): 0}
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            d = dist[(x, y)] + 1
            for dx, dy in dirs:
                nx = x + dx; ny = y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs and (nx, ny) not in dist:
                    dist[(nx, ny)] = d
                    q.append((nx, ny))
        return dist

    opp_dist = bfs((ox, oy))
    self_dist = bfs((sx, sy))

    def best_for_pos(pos):
        px, py = pos
        sd = bfs(pos)
        best = None
        best_adv = -10**9
        for rx, ry in resources:
            if (rx, ry) in sd and (rx, ry) in opp_dist:
                adv = opp_dist[(rx, ry)] - sd[(rx, ry)]
                if adv > best_adv:
                    best_adv = adv
                    best = (rx, ry)
        return best, best_adv

    if resources:
        target, _ = best_for_pos((sx, sy))
        if target is None:
            tx, ty = min(resources, key=lambda r: abs(r[0] - sx) + abs(r[1] - sy))
        else:
            tx, ty = target
    else:
        tx, ty = (w // 2, h // 2)

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx = sx + dx; ny = sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy
            dx = 0; dy = 0
        if resources:
            _, adv = best_for_pos((nx, ny))
            # Also keep moving toward a likely target.
            man = abs(tx - nx) + abs(ty - ny)
            val = 1000 * adv - man
        else:
            val = - (abs(tx - nx) + abs(ty - ny))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]