def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def xy(v, d=(0, 0)):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        return d

    sx, sy = xy(observation.get("self_position", [0, 0]))
    ox, oy = xy(observation.get("opponent_position", [0, 0]))
    role = observation.get("self_role", "pursuer")

    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
        elif isinstance(o, dict) and "x" in o and "y" in o:
            x, y = int(o["x"]), int(o["y"])
        else:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def blocked(x, y):
        return not (0 <= x < w and 0 <= y < h) or (x, y) in obstacles

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def wall_bias(x, y):
        # Prefer states that "open space" near obstacles (evade wall-running).
        s = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles:
                    s += 2
        # Also slightly prefer staying away from borders
        s += (x == 0) + (x == w - 1) + (y == 0) + (y == h - 1)
        return s

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        d = manh(nx, ny, ox, oy)
        if role == "pursuer":
            # If we can capture, do it.
            score = -d * 1000 - wall_bias(nx, ny) * 5
            # Extra tie-break: avoid moving away from opponent in x/y individually.
            score += (abs(nx - ox) < abs(sx - ox) or abs(ny - oy) < abs(sy - oy)) * 3
            if best_score is None or score > best_score:
                best_score, best_move = score, (dx, dy)
        else:
            # Evader: maximize distance; avoid hugging obstacles/borders that lead to wall chains.
            score = d * 1000 - wall_bias(nx, ny) * 20
            # Prefer progressing toward the farthest corner deterministically.
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            farx, fary = max(corners, key=lambda c: manh(c[0], c[1], sx, sy))
            score += manh(nx, ny, farx, fary) * 2
            if best_score is None or score > best_score:
                best_score, best_move = score, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]