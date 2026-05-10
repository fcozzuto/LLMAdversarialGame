def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    opponent_role = str(observation.get("opponent_role") or "").lower()
    if "evad" in self_role or self_role == "evader":
        mode = "evade"
    elif "purs" in self_role or self_role == "pursuer":
        mode = "pursue"
    else:
        mode = "pursue" if ("evad" in opponent_role or opponent_role == "evader") else "evade"

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(a, b, c, d):
        dx, dy = abs(a - c), abs(b - d)
        return dx + dy

    def cell_score(nx, ny):
        if (nx, ny) in obs:
            return -10**9 if mode == "pursue" else -10**8
        d = dist(nx, ny, ox, oy)
        adj_obs = 0
        for ax, ay in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            if (nx + ax, ny + ay) in obs:
                adj_obs += 1
        # pursuer: get closer; avoid adjacency to obstacles too much (prevents dithering near walls)
        if mode == "pursue":
            return (-d * 10) - adj_obs * 2
        # evader: get farther; also avoid moving into cramped obstacle-adjacent spots
        return (d * 10) - adj_obs * 3

    best = None
    best_sc = -10**18 if mode == "evade" else 10**18
    # deterministic tie-breaker order: deltas list order
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        sc = cell_score(nx, ny)
        if mode == "pursue":
            if sc < best_sc:
                best_sc, best = sc, (dx, dy)
        else:
            if sc > best_sc:
                best_sc, best = sc, (dx, dy)

    if best is None:
        # all moves filtered by bounds; stay
        return [0, 0]
    return [int(best[0]), int(best[1])]