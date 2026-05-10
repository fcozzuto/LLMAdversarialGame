def choose_move(observation):
    sx, sy = (observation.get("self_position") or [0, 0])[:2]
    ox, oy = (observation.get("opponent_position") or [0, 0])[:2]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            try:
                obstacles.add((int(p[0]), int(p[1])))
            except Exception:
                pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def parse_cells(key):
        out = []
        for p in (observation.get(key) or []):
            if p and len(p) >= 2:
                try:
                    x, y = int(p[0]), int(p[1])
                except Exception:
                    continue
                if inb(x, y) and (x, y) not in obstacles:
                    out.append((x, y))
        return out

    unclaimed = parse_cells("unclaimed_cells")
    resources = parse_cells("resources")

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = None

    def sq(a, b): 
        return a * a + b * b

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Target preference: near opponent unclaimed -> resources -> opponent -> stay
        if unclaimed:
            # score using best unclaimed cell from this move
            min_d = 10**18
            for (tx, ty) in unclaimed:
                d = sq(tx - nx, ty - ny)
                if d < min_d:
                    min_d = d
            score = 10**6 - min_d  # closer is better
        elif resources:
            tx, ty = min(resources, key=lambda t: sq(t[0] - nx, t[1] - ny))
            score = 10**6 - sq(tx - nx, ty - ny)
        else:
            # chase opponent
            score = 10**6 - sq(ox - nx, oy - ny)

        # slight bias to avoid staying still unless forced
        if dx == 0 and dy == 0:
            score -= 5

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < tuple(best_move)):
            best_score = score
            best_move = [dx, dy]

    return best_move