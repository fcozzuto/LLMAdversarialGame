def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    def toset(v):
        s = set()
        if v is None:
            return s
        for p in v:
            try:
                x, y = p[0], p[1]
            except Exception:
                continue
            s.add((int(x), int(y)))
        return s

    obstacles = toset(observation.get("obstacles") or [])
    unclaimed = toset(observation.get("unclaimed_cells") or [])
    resources = toset(observation.get("resources") or [])

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist(x1, y1, x2, y2):
        d = x1 - x2
        e = y1 - y2
        return (d if d >= 0 else -d) + (e if e >= 0 else -e)

    best = (0, 0)
    bestv = -10**18

    for dx, dy in moves:
        nx, ny = int(ax + dx), int(ay + dy)
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        v = 0
        d_o = dist(nx, ny, ox, oy)
        v += 300 - 20 * d_o

        if (nx, ny) in unclaimed:
            v += 250
        if (nx, ny) in resources:
            v += 220

        if nx == ox and ny == oy:
            v += 100000

        sx = (w - 1) / 2.0
        sy = (h - 1) / 2.0
        v -= int((nx - sx) * (nx - sx) + (ny - sy) * (ny - sy))

        if v > bestv:
            bestv = v
            best = (dx, dy)

    dx, dy = best
    return [int(dx), int(dy)]