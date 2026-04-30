def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obst.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obst:
                resources.append((x, y))
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

    def man(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    if resources:
        best = None
        bestd = 10**9
        for r in resources:
            d = man((sx, sy), r)
            if d < bestd:
                bestd = d
                best = r
        if best is not None:
            dx = best[0] - sx
            dy = best[1] - sy
            if (dx, dy) in legal:
                return [dx, dy]
            # otherwise move towards resource using closest legal step
            best_move = min(legal, key=lambda t: man((sx+t[0], sy+t[1]), best))
            return [best_move[0], best_move[1]]
        # fallback
        best = min(legal, key=lambda t: (abs((sx+t[0]) - ox) + abs((sy+t[1]) - oy), t[0], t[1]))
        return [best[0], best[1]]

    # no resources: head toward opponent with simple approach but avoid edge
    best = min(legal, key=lambda t: (abs((sx+t[0]) - ox) + abs((sy+t[1]) - oy), t[0], t[1]))
    return [best[0], best[1]]