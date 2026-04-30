def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    legal_next = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal_next.append((nx, ny, dx, dy))

    if not legal_next:
        return [0, 0]

    if not resources:
        # drift to center while avoiding obstacles
        cx, cy = w // 2, h // 2
        best = None
        for nx, ny, dx, dy in legal_next:
            d = cheb(nx, ny, cx, cy)
            key = (d, (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    # Tactical: maximize advantage over opponent for some resource; avoid moves that give opponent the same/greater advantage.
    best_key = None
    best_move = (0, 0)
    for nx, ny, dx, dy in legal_next:
        self_to = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        opp_to_from_current = min(cheb(ox, oy, rx, ry) for rx, ry in resources)
        # Advantage: pick the resource where we are relatively closest.
        adv = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            a = do - ds  # positive means we are closer than opponent
            if adv is None or a > adv:
                adv = a
        # Secondary: prefer smaller distance to our chosen best-adv resource and reduce giving opponent edge.
        score = adv
        # If no positive advantage, still move towards a resource that minimizes opponent lead.
        # Combine deterministically.
        opp_after = opp_to_from_current - self_to
        key = (-score, self_to, -(opp_after), nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]