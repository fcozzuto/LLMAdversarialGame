def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", []) or []
    obstacle_set = {(int(x), int(y)) for x, y in obstacles}
    self_role = str(observation.get("self_role", "")).lower()
    opponent_role = str(observation.get("opponent_role", "")).lower()
    role = "pursuer" if ("pursur" in self_role) or ("evad" not in self_role and "evad" in opponent_role) else "evader"

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None

    def clamp(a, lo, hi):
        return lo if a < lo else hi if a > hi else a

    for dx, dy in deltas:
        nx = clamp(int(sx) + dx, 0, w - 1)
        ny = clamp(int(sy) + dy, 0, h - 1)
        if (nx, ny) in obstacle_set:
            nx, ny = int(sx), int(sy)

        dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        on_top = (nx == ox and ny == oy)

        if role == "pursuer":
            score = (-1000000 if on_top else 0) - dist2
        else:
            score = (1000000 if on_top else 0) + dist2

        if best is None or score > best_score:
            best = (dx, dy)
            best_score = score

    return [int(best[0]), int(best[1])]