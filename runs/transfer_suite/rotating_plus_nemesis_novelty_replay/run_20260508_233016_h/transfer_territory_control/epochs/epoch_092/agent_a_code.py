def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 1)
    h = observation.get("grid_height", 1)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    cx, cy = w // 2, h // 2
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = (-10**18, (0, 0))
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        v = 0
        if (nx, ny) in oppT:
            v += 1000
        elif (nx, ny) in unclaimed:
            v += 300
        elif (nx, ny) in selfT:
            v += 80
        else:
            v += 40
        v += (80 - dist(nx, ny, cx, cy))  # toward center
        v += (dist(sx, sy, ox, oy) - dist(nx, ny, ox, oy)) * 2  # keep away from opponent
        if (nx, ny) == (ox, oy):
            v -= 10000
        if v > best[0] or (v == best[0] and (dx, dy) < best[1]):
            best = (v, (dx, dy))
    return [int(best[1][0]), int(best[1][1])]