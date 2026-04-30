def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles", []) or []:
        try:
            px, py = int(p[0]), int(p[1])
            if inb(px, py):
                obst.add((px, py))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obst:
                resources.append((rx, ry))
        except:
            pass

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(a, b):
        ax, ay = a; bx, by = b
        dx = abs(ax - bx); dy = abs(ay - by)
        return dx if dx > dy else dy

    remaining = int(observation.get("remaining_resource_count", len(resources)) or len(resources))

    if resources:
        best = None
        bestd = 10**9
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            for rx, ry in resources:
                d = max(abs(rx - nx), abs(ry - ny))
                if d < bestd:
                    bestd = d
                    best = (dx, dy)
        if best is not None:
            return [best[0], best[1]]

    # Fallback: move away from opponent if possible
    away = None
    mind = -1
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d2 = max(abs(ox - nx), abs(oy - ny))
        if d2 > mind:
            mind = d2
            away = (dx, dy)
    if away:
        return [away[0], away[1]]

    return [0, 0]