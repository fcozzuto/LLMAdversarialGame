def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def sset(key):
        out = set()
        for p in observation.get(key) or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    oppT = sset("opponent_territory")
    un = sset("unclaimed_cells")
    ourT = sset("self_territory")

    ox, oy = observation.get("opponent_position") or (sx, sy)
    ox, oy = int(ox), int(oy)

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    best_score = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        score = 0
        if (nx, ny) in oppT:
            score += 10**6
        if (nx, ny) in un:
            score += 10**5
        if (nx, ny) in ourT:
            score += 1000
        if un:
            md = min(dist(nx, ny, ux, uy) for ux, uy in un if inb(ux, uy) or True)
            score -= md
        else:
            score -= dist(nx, ny, ox, oy)
        if score > best_score:
            best_score = score
            best = [dx, dy]
    return best if best is not None else [0, 0]