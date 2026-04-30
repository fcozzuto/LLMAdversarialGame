def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    ti = int(observation.get("turn_index") or 0)
    if ti & 1:
        moves = moves[4:] + moves[:4]

    best_dxdy = (0, 0)
    if resources:
        best_val = -10**18
        # Prefer the move that maximizes opponent disadvantage while still approaching a resource.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            val = 0
            # Use top few resources to keep logic small/deterministic.
            scored = []
            for rx, ry in resources:
                d_self = cheb(nx, ny, rx, ry)
                d_opp = cheb(ox, oy, rx, ry)
                advantage = d_opp - d_self  # higher => better
                scored.append((advantage, -d_self, rx, ry))
            scored.sort(reverse=True)
            for k in range(min(4, len(scored))):
                adv, negd, rx, ry = scored[k]
                d_self = -negd
                # Strongly prefer moves that close in on resources that are closer to us than them.
                val += (adv * 10) - d_self
                # Small tie-break toward more central resources deterministically.
                cx, cy = (w - 1) // 2, (h - 1) // 2
                val += -0.1 * cheb(rx, ry, cx, cy)
            if val > best_val:
                best_val = val
                best_dxdy = (dx, dy)
    else:
        # No visible resources: head deterministically to center unless it would collide with obstacles.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best_val = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, cx, cy)
            # Slightly prefer moving away from opponent to avoid contesting empty lanes.
            da = cheb(nx, ny, ox, oy)
            val = -d + 0.05 * da
            if val > best_val:
                best_val = val
                best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]