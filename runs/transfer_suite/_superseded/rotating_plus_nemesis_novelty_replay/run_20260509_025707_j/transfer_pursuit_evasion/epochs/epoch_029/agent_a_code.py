def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    if w < 2 or h < 2 or not isinstance(sp, (list, tuple)) or not isinstance(op, (list, tuple)) or len(sp) < 2 or len(op) < 2:
        return [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "pursuer").lower()
    is_evader = role == "evader"

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def obs_neigh_count(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                c += 1
        return c

    best_score = None
    best_move = [0, 0]
    prefer = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    prefer = [m for m in prefer if m in deltas] + [m for m in deltas if m not in prefer]

    for dx, dy in prefer:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        dist = cheb(nx, ny, ox, oy)

        # If roles are assigned, the learner should chase (pursuer) or evade (evader).
        # Score = lower is better for pursuer; higher is better for evader, converted below.
        if is_evader:
            # Evader: maximize distance, but avoid getting squeezed near obstacles.
            score = -dist * 10 + obs_neigh_count(nx, ny) * 2
        else:
            # Pursuer: minimize distance; prefer positions with fewer nearby obstacles (clean approach)
            # and that reduce opponent's immediate "escape" options via local obstacle density.
            score = dist * 10 + obs_neigh_count(nx, ny) * 2

        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]