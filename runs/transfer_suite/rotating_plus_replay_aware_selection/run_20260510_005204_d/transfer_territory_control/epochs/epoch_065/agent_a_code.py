def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_terr = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            self_terr.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    opp_d = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            opp_d.append((cheb(nx, ny, ox, oy), dx, dy))
    if not opp_d:
        return [0, 0]

    best = None
    best_score = -10**18
    any_unclaimed = bool(unclaimed)
    for d, dx, dy in opp_d:
        nx, ny = sx + dx, sy + dy
        score = 0
        score += d * 3  # prefer farther from opponent
        if (nx, ny) in self_terr:
            score += 5
        if any_unclaimed:
            if (nx, ny) in unclaimed:
                score += 50
            else:
                md = 10**9
                # check nearby unclaimed cells only for brevity/determinism
                for ux, uy in unclaimed:
                    dd = cheb(nx, ny, ux, uy)
                    if dd < md:
                        md = dd
                        if md == 0:
                            break
                if md < 10**9:
                    score += max(0, 20 - md)
        if best is None or score > best_score or (score == best_score and (dx, dy) < (best[1], best[2])):
            best_score = score
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]