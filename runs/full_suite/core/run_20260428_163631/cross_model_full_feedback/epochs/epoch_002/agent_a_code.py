def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cur_res = [tuple(r) for r in resources if tuple(r) not in obstacles]
    if cur_res:
        targets = cur_res
    else:
        targets = []

    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        self_to_opp = md(nx, ny, ox, oy)
        if targets:
            sc = -10**18
            for rx, ry in targets:
                ds = md(nx, ny, rx, ry)
                do = md(ox, oy, rx, ry)
                s = (do - ds) * 10 - ds - self_to_opp // 2
                if s > sc:
                    sc = s
            # small tie-break: prefer closer to some resource
            near = min(md(nx, ny, rx, ry) for rx, ry in targets)
            score = sc - near * 0.01
        else:
            # No resources: move to maximize distance from opponent while keeping center pressure
            cx = (w - 1) // 2
            cy = (h - 1) // 2
            score = self_to_opp * 5 - md(nx, ny, cx, cy)
        if score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]