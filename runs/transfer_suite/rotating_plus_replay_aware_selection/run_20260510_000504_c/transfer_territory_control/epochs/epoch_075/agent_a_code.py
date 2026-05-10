def choose_move(observation):
    w = int(observation.get("grid_width", 0))
    h = int(observation.get("grid_height", 0))
    if w <= 0 or h <= 0:
        return [0, 0]
    sx, sy = observation.get("self_position", (w // 2, h // 2))
    sx, sy = int(sx), int(sy)

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_pos = observation.get("opponent_position", None)
    if opp_pos is not None:
        ox, oy = int(opp_pos[0]), int(opp_pos[1])
    else:
        ox, oy = sx, sy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def best_step(tx, ty):
        best = None
        bestv = 10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = md(nx, ny, tx, ty)
            if v < bestv or (v == bestv and (nx, ny) < best):
                bestv = v
                best = (nx, ny)
        if best is None:
            return [0, 0]
        nx, ny = best
        return [nx - sx, ny - sy]

    target = None
    if resources:
        cand = []
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry):
                cand.append((md(sx, sy, rx, ry), rx, ry))
        if cand:
            cand.sort()
            target = (cand[0][1], cand[0][2])

    if target is None:
        frontier = []
        if self_terr and unclaimed:
            for x, y in self_terr:
                for dx, dy in dirs[:-1]:
                    nx, ny = x + dx, y + dy
                    if inb(nx, ny) and (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                        frontier.append((md(sx, sy, nx, ny), nx, ny))
            if frontier:
                frontier.sort()
                target = (frontier[0][1], frontier[0][2])

    if target is None:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        target = (cx, cy)

    step = best_step(target[0], target[1])

    nx, ny = sx + step[0], sy + step[1]
    if step == [0, 0] and unclaimed and self_terr:
        for dx, dy in dirs:
            tx, ty = sx + dx, sy + dy
            if inb(tx, ty) and (tx, ty) in unclaimed and (tx, ty) not in obstacles:
                return [dx, dy]
    return step if inb(nx, ny) and (nx, ny) not in obstacles else [0, 0]