def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = str(observation.get("self_role", "") or "").lower()
    opponent_role = str(observation.get("opponent_role", "") or "").lower()
    # In pursuit_evasion, treat "evader" as fleeing; otherwise chase.
    evader = ("evad" in self_role) or ("escape" in self_role) or ("run" in self_role) or ("purs" in opponent_role and "evad" not in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # For deterministic tie-breaking: prefer larger dx then larger dy in a fixed order.
    best_move = (0, 0)
    best_val = -10**18 if evader else 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            nx, ny = sx, sy
            dx, dy = 0, 0
        if (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0

        d = md(nx, ny, ox, oy)

        if evader:
            # Flee: maximize distance; also bias toward moving away from opponent.
            # Avoid pushing into corners that are closer to opponent.
            bias = 0
            bias += 0 if nx == sx else (1 if (nx - ox) * (sx - ox) >= 0 else -1)
            bias += 0 if ny == sy else (1 if (ny - oy) * (sy - oy) >= 0 else -1)
            val = d * 10 + bias
            if val > best_val or (val == best_val and (dx, dy) > best_move):
                best_val = val
                best_move = (dx, dy)
        else:
            # Pursuer: minimize distance; if tied, bias toward alignment with opponent.
            align = 0
            align += 1 if (dx == 0 and sx == ox) else 0
            align += 1 if (dy == 0 and sy == oy) else 0
            align += 2 if (dx != 0 and ((sx + dx) - ox) * (sx - ox) <= 0) else 0
            align += 2 if (dy != 0 and ((sy + dy) - oy) * (sy - oy) <= 0) else 0
            val = d * 10 - align
            if val < best_val or (val == best_val and (dx, dy) > best_move):
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]