def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    is_pursuer = (observation.get("self_role", "pursuer") == "pursuer")

    def dist2(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy

    def edge_score(x, y):
        # Prefer positions closer to an edge (evader-style) to stay hard to corner.
        return min(x, w - 1 - x, y, h - 1 - y)

    best = None
    best_val = None

    # Intended direction from pursuer to evader/opponent.
    vx = 0 if ox == sx else (1 if ox > sx else -1)
    vy = 0 if oy == sy else (1 if oy > sy else -1)

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue

            d = dist2(nx, ny, ox, oy)
            if is_pursuer:
                # Greedy capture pressure; discourage "stalling" while still safe.
                val = (-d) - (0.25 if dx == 0 and dy == 0 else 0.0)
                # Slightly prefer moving in the general direction toward opponent.
                val += 0.05 * (1 if dx == vx else 0)
                val += 0.05 * (1 if dy == vy else 0)
            else:
                # Evade by increasing distance; also bias toward consistent zigzag continuation:
                # move along the sign of the vector away from opponent when possible.
                away_x = 0 if sx == ox else (1 if sx > ox else -1)
                away_y = 0 if sy == oy else (1 if sy > oy else -1)
                val = d
                val += 0.08 * (1 if dx == away_x else 0)
                val += 0.08 * (1 if dy == away_y else 0)
                # Prefer being near an edge (harder for pursuer to align in zigzags).
                val += 0.02 * (-edge_score(nx, ny))

            if best_val is None or val > best_val:
                best_val = val
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]