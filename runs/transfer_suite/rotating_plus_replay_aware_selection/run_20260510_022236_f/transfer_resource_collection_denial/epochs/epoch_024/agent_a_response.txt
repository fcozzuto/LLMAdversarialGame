def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_val = -10**18
    best_move = [0, 0]

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Immediate deny/collect pressure: one-step greedy over resources.
        move_val = -10**18
        for rx, ry in resources:
            rx, ry = int(rx), int(ry)
            if not inb(rx, ry) or (rx, ry) in obs:
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            if nx == rx and ny == ry:
                val = 10**9 + (od - sd)  # prioritize instant collection
            else:
                val = (od - sd) * 1000 - sd  # prefer resources we can reach sooner than opponent
            if val > move_val:
                move_val = val

        # If there are no resources, just stay.
        if resources == []:
            move_val = 0

        if move_val > best_val:
            best_val = move_val
            best_move = [dxm, dym]

    if resources == []:
        return [0, 0]
    return best_move