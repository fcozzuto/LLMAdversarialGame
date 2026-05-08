def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))
    sx, sy, px, py = int(sx), int(sy), int(px), int(py)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    blocked = set()
    for b in observation.get("obstacles") or []:
        try:
            x, y = int(b[0]), int(b[1])
            if inb(x, y):
                blocked.add((x, y))
        except Exception:
            pass

    self_term = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        d = (nx - px) * (nx - px) + (ny - py) * (ny - py)
        score = -d
        if (nx, ny) in unclaimed:
            score += 50
        if (nx, ny) in self_term:
            score += 10
        if best is None or score > best_score or (score == best_score and (dx, dy) == best):
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best