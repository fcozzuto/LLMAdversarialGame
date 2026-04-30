def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    best_move = (0, 0)
    best_val = -10**18
    best_aux = 10**18

    cx, cy = w // 2, h // 2

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if resources:
            # Choose a target that we can reach quickly while keeping opponent farther.
            val = -dist(nx, ny, ox, oy) * 0.05
            aux = 10**18
            for tx, ty in resources:
                ds = dist(nx, ny, tx, ty)
                do = dist(ox, oy, tx, ty)
                if ds == 0:
                    gain = 10**6
                else:
                    gain = (do - ds) * 50.0 - ds * 10.0
                # Encourage moving generally toward resources while still contesting.
                gain += (cx - tx) * 0.01 + (cy - ty) * 0.01
                if gain > val:
                    val = gain
                    aux = ds
            # Slight preference for shorter path if values tie.
            val -= aux * 0.01
        else:
            # No visible resources: move toward center but keep distance from opponent.
            val = -dist(nx, ny, cx, cy) + dist(nx, ny, ox, oy) * 0.02
            aux = dist(nx, ny, cx, cy)

        if val > best_val or (val == best_val and aux < best_aux):
            best_val = val
            best_aux = aux
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]