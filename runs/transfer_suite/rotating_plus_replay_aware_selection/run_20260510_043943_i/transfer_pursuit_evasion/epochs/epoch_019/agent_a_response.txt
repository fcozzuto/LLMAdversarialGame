def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    self_role = (observation.get("self_role", "") or "").lower()

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def sgn(z):
        return 0 if z == 0 else (1 if z > 0 else -1)

    pursuer = ("pursur" in self_role) or (self_role == "pursuer") or ("hunter" in self_role) or ("pursuer" in self_role)
    target_dx = sgn(ox - sx)
    target_dy = sgn(oy - sy)

    best = (0, 0)
    best_score = -10**18 if pursuer else 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        dxo = nx - ox
        dyo = ny - oy
        dist2 = dxo * dxo + dyo * dyo
        align = 1 if (dx == target_dx and dy == target_dy) else 0

        if not pursuer:
            # Avoid stepping onto the pursuer (instant capture for evader)
            if nx == ox and ny == oy:
                score = -10**12
            else:
                score = dist2 * 10.0 + align * 1.0 - (abs(dx) + abs(dy)) * 0.02
                if score > best_score:
                    best_score = score
                    best = (dx, dy)
        else:
            # Chase: minimize squared distance; prefer alignment to reduce zigzag
            score = -dist2 * 10.0 + align * 1.0 - (abs(dx) + abs(dy)) * 0.02
            if score > best_score:
                best_score = score
                best = (dx, dy)

    return [int(best[0]), int(best[1])]