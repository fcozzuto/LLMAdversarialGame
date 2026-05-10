def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    ox, oy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (ox, oy))

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells", [])))
    resources = list(map(tuple, observation.get("resources", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    candidates = [c for c in unclaimed if c not in obstacles] or [c for c in resources if c not in obstacles]
    if candidates:
        # Prefer nearest unclaimed; tie-break by lexicographic
        tx, ty = min(candidates, key=lambda c: (abs(c[0] - ox) + abs(c[1] - oy), c[0], c[1]))
        target = (tx, ty)
    else:
        # Fallback: go for closest opponent territory cell, else closest corner
        opp_cells = [c for c in opp_terr if c not in obstacles]
        if opp_cells:
            tx, ty = min(opp_cells, key=lambda c: (abs(c[0] - ox) + abs(c[1] - oy), c[0], c[1]))
            target = (tx, ty)
        else:
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            target = min(corners, key=lambda c: (abs(c[0] - ox) + abs(c[1] - oy), c[0], c[1]))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_score = None
    best_move = (0, 0)

    for dx, dy in dirs:
        nx, ny = ox + dx, oy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dist = abs(target[0] - nx) + abs(target[1] - ny)
        # Deterministic tie-break: prefer stepping into opponent territory (flipping), then reduce distance,
        # then prefer forward-ish moves, then lexicographic.
        into_opp = 1 if (nx, ny) in opp_terr else 0
        into_self = 1 if (nx, ny) in self_terr else 0
        toward_dx = 0 if dx == 0 else (1 if (target[0] - ox) * dx > 0 else 0)
        toward_dy = 0 if dy == 0 else (1 if (target[1] - oy) * dy > 0 else 0)
        score = (into_opp, -dist, toward_dx + toward_dy, -into_self, -nx, -ny)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]