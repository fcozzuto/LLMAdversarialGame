def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def pack(p):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return int(p[0]), int(p[1])
        if isinstance(p, dict):
            if "x" in p and "y" in p:
                return int(p["x"]), int(p["y"])
            pos = p.get("position")
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                return int(pos[0]), int(pos[1])
        return None

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        t = pack(p)
        if t:
            obstacles.add(t)

    resources = []
    for p in observation.get("resources", []) or []:
        t = pack(p)
        if t:
            resources.append(t)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    target = None
    bestd = 10**9
    for rx, ry in resources:
        d = abs(rx - sx) + abs(ry - sy)
        if d < bestd:
            bestd = d
            target = (rx, ry)

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if target is not None:
            dist_to = abs(target[0] - nx) + abs(target[1] - ny)
            dist_opp = abs(ox - nx) + abs(oy - ny)
            val = -(dist_to * 10) + dist_opp
        else:
            val = -(abs(ox - nx) + abs(oy - ny))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]