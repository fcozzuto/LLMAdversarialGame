def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    pursuer = ("pursu" in self_role) or ("chase" in self_role) or ("hunter" in self_role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic preference: axial, then diagonals; avoid staying unless needed
    pref = [(0, -1), (-1, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    moves = [m for m in pref if m in moves] + [m for m in moves if m not in pref]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best = None
    best_score = None

    # If evader, also softly prefer staying near open space by penalizing proximity to obstacles.
    def obst_prox(nx, ny):
        # count obstacles in 1-step neighborhood (small and deterministic)
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (nx + dx, ny + dy) in obstacles:
                    c += 1
        return c

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = cheb(nx, ny, ox, oy)

        # Avoid moving onto immediate capture adjacency for evader (even though capture_radius=0).
        # For pursuer, strongly prefer decreasing distance.
        if pursuer:
            # primary: minimize distance; secondary: minimize obstacle proximity; tertiary: avoid staying
            score = (-dist) * 1000 - obst_prox(nx, ny) * 10 - (1 if dx == 0 and dy == 0 else 0)
        else:
            # primary: maximize distance; secondary: maximize openness; tertiary: avoid edges-to-edge trapping
            open_score = obst_prox(nx, ny)
            # prefer staying away from opponent while also not hugging obstacles
            score = (dist) * 1000 - open_score * 10 - (1 if dx == 0 and dy == 0 else 0)
            # slight preference to avoid corners when possible
            corner = (nx == 0 or nx == w - 1) and (ny == 0 or ny == h - 1)
            score -= 3 if corner else 0

        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]