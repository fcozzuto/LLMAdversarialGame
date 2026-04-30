def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If no resources: head to a corner away from opponent, but keep within board/avoid obstacles
    if not resources:
        # Choose among 4 corners deterministically
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        bestc = (sx, sy)
        bestv = -10**9
        for cx, cy in corners:
            if not inb(cx, cy): 
                continue
            v = cheb(cx, cy, ox, oy) - cheb(cx, cy, sx, sy)
            if v > bestv:
                bestv, bestc = v, (cx, cy)
        tx, ty = bestc
    else:
        # Target the resource with maximum "steal advantage": opponent farther than us, also progress vs our distance
        bestt = resources[0]
        bestv = -10**18
        for rx, ry in resources:
            d1 = cheb(sx, sy, rx, ry)
            d2 = cheb(ox, oy, rx, ry)
            # Prefer closer to us, farther from opponent; small tie-breaker to center to avoid oscillation
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            center = -((rx - cx) ** 2 + (ry - cy) ** 2) * 1e-4
            v = (d2 - d1) * 1000 - d1 + center
            if v > bestv:
                bestv, bestt = v, (rx, ry)
        tx, ty = bestt

    # One-step greedy move towards target with opponent-aware scoring and obstacle avoidance
    cand = [(-1, -1),(0, -1),(1, -1),(-1, 0),(0, 0),(1, 0),(-1, 1),(0, 1),(1, 1)]
    bestm = (0, 0)
    bests = -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        oppd = cheb(ox, oy, nx, ny)
        opp_to_target = cheb(ox, oy, tx, ty)
        # Encourage: reduce distance to target; discourage: moving into squares too close to opponent; slight avoid adjacency with opponent
        score = -myd * 1000 + opp_to_target * 5 - min(4, oppd) * 20
        # If landing on a resource, huge
        if (nx, ny) in resources:
            score += 10**9
        # Slightly prefer staying closer to line to target
        score += -(abs((tx - nx)) + abs((ty - ny))) * 0.1
        if score > bests:
            bests, bestm = score, (dx, dy)
    return [int(bestm[0]), int(bestm[1])]