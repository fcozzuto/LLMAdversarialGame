def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "") or "").lower()
    opp_role = str(observation.get("opponent_role", "") or "").lower()
    self_is_evader = ("evad" in self_role) or (("agent" in self_role) and ("evad" in opp_role))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp_inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def obs_proximity(nx, ny):
        if not obstacles:
            return 99
        md = 99
        for bx, by in obstacles:
            d = abs(nx - bx) + abs(ny - by)
            if d < md:
                md = d
        return md

    best = None
    best_val = None
    best_tie = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not clamp_inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        cheb = max(abs(nx - ox), abs(ny - oy))
        eu2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        prox = obs_proximity(nx, ny)

        if self_is_evader:
            val = cheb
            tie = (eu2, -prox)  # prefer farther, then fewer close obstacles
            # maximize val; for tie compare smaller eu2 and larger prox
            if best is None or (val > best_val) or (val == best_val and tie < best_tie):
                best, best_val, best_tie = (dx, dy), val, tie
        else:
            val = -cheb
            tie = (eu2, -prox)  # maximize -cheb => minimize cheb; then reduce eu2, avoid obstacles
            if best is None or (val > best_val) or (val == best_val and tie < best_tie):
                best, best_val, best_tie = (dx, dy), val, tie

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]