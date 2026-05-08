def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []))
    unclaimed = [(int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or [])]

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    def dman(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    targets = unclaimed if unclaimed else (list(opp_terr) if opp_terr else [(ox, oy)])
    if not targets:
        return [0, 0]

    primary = min(targets, key=lambda t: (dman(sx, sy, t[0], t[1]), t[0], t[1]))

    best = None
    best_key = None
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    tx, ty = primary

    for dx, dy in moves:
        if not (dx in (-1, 0, 1) and dy in (-1, 0, 1)):
            continue
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        dist = dman(nx, ny, tx, ty)
        prev_dist = dman(sx, sy, tx, ty)
        improved = prev_dist - dist

        gain = 0
        if (nx, ny) in opp_terr:
            gain += 3  # likely flip on entry
        if (nx, ny) in unclaimed:
            gain += 2  # likely capture/claim expansion
        if (nx, ny) in self_terr:
            gain += 0  # safe but not expanding

        edge = 0
        if nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1:
            edge = 1

        # Deterministic preference: maximize (gain + edge + improved), then minimize distance, then lexicographic move
        key = (-(gain + edge + improved), dist, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    return best if best is not None else [0, 0]