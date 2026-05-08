def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evader" in sr) or ("runner" in sr) or (("pursuer" not in sr) and ("evader" in orr))

    moves = [(0, 0), (1, 1), (1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0), (-1, -1)]

    obs_list = list(obstacles)
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def wall_bias(x, y):
        # encourages/avoids hugging walls depending on role
        dleft, dright, dbot, dtop = x, (w - 1 - x), y, (h - 1 - y)
        m = min(dleft, dright, dbot, dtop)
        if self_is_evader:
            return -2.0 * m  # prefer larger distance from walls
        return 2.0 * m       # prefer smaller distance from walls (trap runner)

    def obstacle_penalty(x, y):
        if not obs_list:
            return 0.0
        md = 10**9
        for px, py in obs_list:
            d = abs(x - px) + abs(y - py)
            if d < md:
                md = d
        if md <= 0:
            return 1e6
        # stronger penalty near obstacles to avoid getting "wall stuck"
        return 3.0 / md

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d_before = man(sx, sy, ox, oy)
        d_after = man(nx, ny, ox, oy)
        dp = obstacle_penalty(nx, ny)
        wb = wall_bias(nx, ny)

        if self_is_evader:
            # maximize distance; also bias toward moving along the longer axis away from pursuer
            ax = abs(ox - nx)
            ay = abs(oy - ny)
            stretch = max(ax, ay) - min(ax, ay)
            val = (d_after * 3.0) + (stretch * 0.3) + wb - dp
        else:
            # minimize distance; include "approach momentum" and cornering pressure
            approach = (d_before - d_after)  # positive if getting closer
            val = (-d_after * 3.0) + (approach * 2.0) + wb - dp

        if bestv is None or val > bestv:
            bestv = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]