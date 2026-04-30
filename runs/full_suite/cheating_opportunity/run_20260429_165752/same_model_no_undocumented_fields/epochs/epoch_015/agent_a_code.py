def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            ex, ey = int(o[0]), int(o[1])
            if 0 <= ex < w and 0 <= ey < h:
                obstacles.add((ex, ey))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    r_opp = min(resources, key=lambda r: md(ox, oy, r[0], r[1]))
    r_adv = max(resources, key=lambda r: (md(ox, oy, r[0], r[1]) - md(sx, sy, r[0], r[1]), -md(sx, sy, r[0], r[1])))
    adv = md(ox, oy, r_adv[0], r_adv[1]) - md(sx, sy, r_adv[0], r_adv[1])

    target = r_adv if adv > 0 else r_opp

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_self = md(nx, ny, target[0], target[1])
        d_opp = md(nx, ny, ox, oy)
        # If contesting (no advantage), prefer moves that keep distance while reducing our path to the opponent-nearest resource.
        # Otherwise, prefer moves that rapidly close on our advantageous resource and also keep away from opponent.
        val = (d_self, -d_opp) if adv > 0 else (d_self, -d_opp)
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]