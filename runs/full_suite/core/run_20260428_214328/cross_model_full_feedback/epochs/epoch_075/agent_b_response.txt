def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = (int(x) for x in observation.get("self_position", [0, 0]))
    ox, oy = (int(x) for x in observation.get("opponent_position", [w - 1, h - 1]))
    obst = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))
    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))
    def dist_cheb(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))
    best_res = None
    bestd = None
    for rx, ry in resources:
        d = dist_cheb((sx, sy), (rx, ry))
        if bestd is None or d < bestd or (d == bestd and (rx, ry) < best_res):
            best_res = (rx, ry)
            bestd = d
    if best_res is not None:
        dx = 0 if best_res[0] == sx else (1 if best_res[0] > sx else -1)
        dy = 0 if best_res[1] == sy else (1 if best_res[1] > sy else -1)
        return [dx, dy]
    center = (w // 2, h // 2)
    dx = 0 if center[0] == sx else (1 if center[0] > sx else -1)
    dy = 0 if center[1] == sy else (1 if center[1] > sy else -1)
    cand = [(dx, dy)]
    # avoid obstacles if possible
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst
    for ddx in (-1, 0, 1):
        for ddy in (-1, 0, 1):
            nx, ny = sx + ddx, sy + ddy
            if (ddx, ddy) == (0, 0): 
                continue
            if inb(nx, ny):
                cand.append((0 if ddx==0 else (1 if ddx>0 else -1),
                             0 if ddy==0 else (1 if ddy>0 else -1)))
    # Ensure returns valid move within allowed set
    for mv in cand:
        dx, dy = mv
        if dx in (-1,0,1) and dy in (-1,0,1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h:
                if (nx, ny) not in obst:
                    return [dx, dy]
    return [0, 0]