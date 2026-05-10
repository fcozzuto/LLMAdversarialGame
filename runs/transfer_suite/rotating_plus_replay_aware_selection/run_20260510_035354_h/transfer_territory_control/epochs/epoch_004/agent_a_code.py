def choose_move(observation):
    ax, ay = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    turn = observation.get("turn_index", 0)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for x, y in obstacles:
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    unclaimed = observation.get("unclaimed_cells") or []
    un = set()
    for x, y in unclaimed:
        if 0 <= x < w and 0 <= y < h:
            un.add((x, y))

    my_t = observation.get("self_territory") or []
    op_t = observation.get("opponent_territory") or []
    my_set = set((x, y) for x, y in my_t if 0 <= x < w and 0 <= y < h)
    op_set = set((x, y) for x, y in op_t if 0 <= x < w and 0 <= y < h)

    dirs = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_op(x, y):
        for dx, dy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)):
            nx, ny = x + dx, y + dy
            if (nx, ny) in op_set:
                return True
        return False

    best_move = [0, 0]
    best_val = -10**9

    # Deterministic "pressure": occasionally bias toward opponent territory.
    bias_op = (turn % 6) in (3, 4)

    for dx, dy in dirs:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            val = -10**8
        else:
            val = 0
            if (nx, ny) in un:
                val += 7
            if (nx, ny) in my_set:
                val += 2
            if (nx, ny) in op_set:
                val += 10 + (2 if bias_op else 0)
            if adj_op(nx, ny):
                val += 4
            # Encourage moving toward the most contested region: near both territories.
            # Use simple distance to nearest opponent territory cell (approx via corners fallback).
            if not op_set:
                val += -(abs(nx - (w//2)) + abs(ny - (h//2))) * 0.01
            else:
                # small deterministic approximation: compare to nearest of up to 3 anchor points from opponent
                anchors = list(op_set)
                ax1, ay1 = anchors[0]
                ax2, ay2 = anchors[len(anchors)//2]
                ax3, ay3 = anchors[-1]
                d = min(abs(nx-ax1)+abs(ny-ay1), abs(nx-ax2)+abs(ny-ay2), abs(nx-ax3)+abs(ny-ay3))
                val += max(0, 6 - d) * 0.6
            # Avoid "sticking" unless no better option exists.
            if dx == 0 and dy == 0:
                val -= 1
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move