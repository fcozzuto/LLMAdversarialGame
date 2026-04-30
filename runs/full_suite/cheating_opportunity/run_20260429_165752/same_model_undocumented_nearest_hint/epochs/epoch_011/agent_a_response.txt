def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_for(nx, ny):
        if not resources:
            # No visible resources: drift toward center to be well-positioned.
            cx, cy = (W - 1) // 2, (H - 1) // 2
            return -cheb(nx, ny, cx, cy), 0, 0
        # Evaluate each resource by advantage: (opp_dist - my_dist) favoring grabs.
        best = (-10**9, 10**9, 10**9)  # (adv, mydist, oppdist) with lexicographic maximize on adv
        for rx, ry in resources:
            md = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - md
            # Primary: maximize advantage; Secondary: smaller my distance; Tertiary: larger opp distance.
            cand = (adv, -md, od)
            if cand > (best[0], -best[1], best[2]):
                best = (adv, md, od)
        # Convert to (score, mydist, oppdist) where score increases with advantage.
        return best[0], best[1], best[2]

    best_move = (0, 0)
    best_key = (-10**9, 10**9, -10**9)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        s, md, od = best_for(nx, ny)
        # Prefer higher advantage, then closer to resource, then farther from opponent's position to reduce contest.
        key = (s, -md, -od)
        if key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]